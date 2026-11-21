"""Hardware scan (plan P7): find hardware access past ROS and the command gate.

Goes through every tracked file of packages/ and system-files/ (and the root compose /
projectctl), one by one. Text files are searched line by line for direct hardware access
(serial, USB, CAN, I2C, SPI, GPIO, controller SDKs, device files, privileged containers,
device mounts, hardware IPs, external driver code). Binary files (images, models) are
listed as checked (no code). Every finding is rated:

    erlaubt   - driver package behind the command gate, or a sensor (read only)
    Hinweis   - not hardware access past ROS, but worth knowing
    Problem   - hardware access or rights outside a driver package -> report to the owner
    offen     - cannot be checked here (external code cloned at build time)

    python3 tools/hardware_scan.py            # writes docs/hardware_access_report.md
    python3 tools/hardware_scan.py --check    # exit 1 if a finding is rated Problem

Findings in other packages are reported, not changed (plan P7, step 4).
"""

import argparse
from dataclasses import dataclass
import datetime
import os
import re
import subprocess
import sys

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
REPORT = os.path.join(REPO, 'docs', 'hardware_access_report.md')
ROOTS = ['packages', 'system-files', 'compose.yaml', 'projectctl.bash']
SELF = 'tools/hardware_scan.py'

DRIVER_PACKAGES = {'pkg_drive'}          # behind the command gate (profile real only)

RULES = [
    ('serial', re.compile(r'\bimport serial\b|\bfrom serial\b|\bserial\.Serial\b|pyserial')),
    ('usb', re.compile(r'\bpyusb\b|\busb\.core\b|\blibusb\b')),
    ('tty', re.compile(r'/dev/tty[A-Za-z0-9]*|ttyUSB|ttyACM|ttyMotor')),
    ('device file', re.compile(r'/dev/(i2c|spidev|gpio|video|snd|input|js\d|bus/usb|'
                               r'georg_controller)')),
    ('can', re.compile(r'\bimport can\b|\bfrom can\b|socketcan|SocketCAN|\bcan0\b|'
                       r'python-can')),
    ('i2c/smbus', re.compile(r'\bsmbus2?\b|\bi2c\b', re.I)),
    ('spi', re.compile(r'\bspidev\b')),
    ('gpio', re.compile(r'Jetson\.GPIO|RPi\.GPIO|\bgpiod\b|\blgpio\b')),
    ('controller sdk', re.compile(r'tinkerforge|dynamixel_sdk|pib_sdk|pib-sdk|roslibpy')),
    ('hardware ip', re.compile(r'192\.168\.2\.\d+')),
    ('raw socket', re.compile(r'socket\.socket\(')),
    ('audio device', re.compile(r'\bpyaudio\b|PyAudio|sounddevice|ALSA_CARD|PULSE_SERVER',
                                re.I)),
    ('privileged', re.compile(r'privileged:\s*true')),
    ('device mount', re.compile(r'^\s*-\s*/dev[:/]|^\s*devices\s*:|/dev/snd')),
    ('external code', re.compile(r'git clone\s+\S+')),
    ('udev rule', re.compile(r'^\s*(SUBSYSTEM|KERNEL)==')),
    ('cmd_vel publisher', re.compile(r'create_publisher\(\s*Twist\b')),
]


@dataclass
class Finding:
    package: str
    path: str
    line: int
    rule: str
    text: str
    comment: bool = False          # inside a comment or docstring
    rating: str = ''
    reason: str = ''


def package_of(path: str) -> str:
    parts = path.split('/')
    if parts[0] == 'packages' and len(parts) > 1:
        return parts[1]
    return parts[0]


def rate(f: Finding) -> None:
    """Rate one finding (allowed / note / problem / open) with a reason."""
    pkg, rule, path, text = f.package, f.rule, f.path, f.text

    def set_(rating, reason):
        f.rating, f.reason = rating, reason

    if pkg == 'pkg_gestures' and rule == 'controller sdk' and f.comment \
            and ('import' in text) and path.endswith('.py'):
        return set_('Problem', 'Aufruf heute auskommentiert (inaktiv); vor dem Aktivieren '
                               'über ROS-Topics des Stacks führen')
    if path.endswith('.md'):
        return set_('Hinweis', 'nur Dokumentation')
    if f.comment:
        return set_('Hinweis', 'nur Kommentar/Docstring')

    if pkg in DRIVER_PACKAGES:
        if rule == 'external code':
            return set_('offen', 'Treiber-Code (edu_robot) wird beim Bauen geklont, nicht im '
                                 'Repo geprüft; muss cmd_vel abonnieren')
        return set_('erlaubt', 'Treiber-Paket; edu_robot nur in real (sim: sim_mode ohne Treiber), '
                               'hinter twist_mux/twist_limiter')
    if pkg == 'system-files' and rule in ('udev rule', 'tty', 'device file'):
        if 'ttyMotor' in text or '99-pib-motors' in path:
            return set_('Hinweis', 'Motor-Controller-Regel; im Repo nutzt sie kein Paket '
                                   '(vermutlich pib-backend auf dem Pi)')
        return set_('erlaubt', 'Joystick für die Fernsteuerung in pkg_drive (Treiber)')
    if pkg == 'pkg_slam':
        if rule == 'hardware ip':
            return set_('erlaubt', 'Netzwerk-Lidar (SICK), nur lesend, kein Aktor')
        if rule == 'external code':
            return set_('offen', 'Sensor-Treiber (sick_scan_xd, rf2o, scan merger) werden '
                                 'geklont; lesend, nicht im Repo geprüft')
        if rule in ('privileged', 'device mount'):
            return set_('Problem', 'SLAM braucht weder privileged noch /dev (Lidar über '
                                   'Netzwerk); entfernen')
    if pkg == 'pkg_gestures' and rule == 'controller sdk':
        if path.endswith('Dockerfile') or path.endswith('pyproject.toml') or 'README' in path:
            return set_('Problem', 'pib-sdk steuert die Servos des pib direkt (über '
                                   'rosbridge/roslibpy), an Georgs ROS-Stack vorbei')
        if text.lstrip().startswith('#'):
            return set_('Problem', 'Aufruf heute auskommentiert (inaktiv); vor dem '
                                   'Aktivieren über ROS-Topics des Stacks führen')
        return set_('Problem', 'Servo-Ansteuerung an Georgs ROS-Stack vorbei')
    if pkg == 'pkg_task_manager' and rule == 'usb' and 'voice_assistant' in path:
        return set_('Hinweis', 'USB-Bibliothek für das Mikrofon-Array der Spracherkennung, '
                               'kein Bewegungsaktor')
    if pkg == 'pkg_task_manager' and rule == 'audio device':
        return set_('Hinweis', 'Mikrofon/Lautsprecher der Spracherkennung, kein '
                               'Bewegungsaktor')
    if pkg == 'pkg_task_manager' and rule == 'hardware ip':
        return set_('Hinweis', 'IP-Adresse im Text (Doku/Konfiguration), kein Zugriff')
    if rule == 'cmd_vel publisher':
        if pkg == 'pkg_navigation':
            return set_('Hinweis', 'Fahrbefehl über ROS (cmd_vel). Im Profil real per Launch '
                                   'auf cmd_vel/nav umgeleitet -> twist_mux -> twist_limiter '
                                   '-> Treiber')
        if pkg == 'pkg_sim':
            return set_('erlaubt', 'Simulator selbst')
        return set_('Hinweis', 'Fahrbefehl über ROS; läuft über twist_mux/twist_limiter')
    if pkg == 'pkg_task_manager' and rule in ('device mount', 'device file') \
            and ('/dev/snd' in text or rule == 'device mount'):
        return set_('Hinweis', 'nur Audio-Geräte (/dev/snd) für die Spracherkennung, '
                               'kein Bewegungsaktor')
    if rule in ('privileged', 'device mount'):
        if pkg == 'pkg_viz':
            return set_('Problem', 'RViz-Container (nur Profil viz) braucht kein /dev und '
                                   'kein privileged außer für die GPU; einschränken')
        return set_('Problem', 'privileged/Geräte-Zugriff außerhalb eines Treiber-Pakets; '
                               'nicht nötig, entfernen')
    if rule == 'external code':
        return set_('offen', 'beim Bauen geklonter Code, nicht im Repo geprüft')
    if rule == 'hardware ip':
        return set_('Hinweis', 'IP-Adresse (Netzplan/Doku), kein Zugriff im Code')
    if pkg == 'pkg_gestures':
        return set_('Problem', 'Hardware-Zugriff im Gesten-Paket')
    return set_('Problem', f'{rule} außerhalb eines Treiber-Pakets')


def tracked_files():
    out = subprocess.run(['git', 'ls-files', *ROOTS], cwd=REPO, capture_output=True,
                         text=True, check=True).stdout
    return sorted(p for p in out.splitlines() if p != SELF)


def read_text(path):
    with open(os.path.join(REPO, path), 'rb') as f:
        data = f.read()
    if b'\x00' in data[:4096]:
        return None
    try:
        return data.decode('utf-8')
    except UnicodeDecodeError:
        return None


def scan():
    findings, checked = [], []
    for path in tracked_files():
        text = read_text(path)
        if text is None:
            checked.append((path, 'binär (Bild/Modell/Archiv), kein Code'))
            continue
        checked.append((path, f'{text.count(chr(10)) + 1} Zeilen geprüft'))
        in_doc = False
        hash_comments = path.endswith(('.py', '.yaml', '.yml', '.toml', '.sh', '.bash',
                                       '.cfg', '.rules', '.txt', 'Dockerfile', '.bridge'))
        for no, line in enumerate(text.splitlines(), 1):
            stripped = line.strip()
            quotes = stripped.count('"""') + stripped.count("'''")
            comment = in_doc or (hash_comments and stripped.startswith('#')) \
                or (path.endswith('.py') and quotes > 0)
            if path.endswith('.py') and quotes % 2 == 1:
                in_doc = not in_doc
            for name, pattern in RULES:
                if pattern.search(line):
                    f = Finding(package_of(path), path, no, name, stripped[:120], comment)
                    rate(f)
                    findings.append(f)
    return findings, checked


def report(findings, checked) -> str:
    today = datetime.date.today().isoformat()
    by = {}
    for f in findings:
        by.setdefault(f.rating, []).append(f)
    problems = by.get('Problem', [])
    lines = [
        '# Hardware-Zugriffs-Bericht (P7)',
        '',
        f'Erzeugt am {today} von `tools/hardware_scan.py`. {len(checked)} Dateien einzeln '
        f'geprüft, {len(findings)} Fundstellen.',
        '',
        '**Profil `real`: ' + ('NICHT freigegeben** – es gibt offene Probleme (unten). '
                               'Funde in fremden Paketen werden gemeldet, nicht umgebaut.'
                               if problems else 'freigegeben** – keine Probleme.'),
        '',
        '| Bewertung | Anzahl |',
        '| --- | --- |',
    ]
    for rating in ('Problem', 'offen', 'Hinweis', 'erlaubt'):
        lines.append(f'| {rating} | {len(by.get(rating, []))} |')
    lines += ['', '## Meldungen an die Paket-Verantwortlichen', '']
    seen = {}
    for f in problems + by.get('offen', []):
        seen.setdefault((f.package, f.rating, f.reason), []).append(f'{f.path}:{f.line}')
    for (pkg, rating, reason), where in sorted(seen.items()):
        lines.append(f'- **{pkg}** ({rating}): {reason}. Stellen: '
                     + ', '.join(f'`{w}`' for w in where[:6])
                     + (f' und {len(where) - 6} weitere' if len(where) > 6 else ''))
    lines += ['', '## Alle Fundstellen', '',
              '| Paket | Datei | Zeile | Fundstelle | Regel | Bewertung | Begründung |',
              '| --- | --- | --- | --- | --- | --- | --- |']
    for f in sorted(findings, key=lambda f: (f.rating != 'Problem', f.package, f.path, f.line)):
        text = f.text.replace('|', '\\|').replace('`', "'")
        lines.append(f'| {f.package} | `{f.path}` | {f.line} | `{text}` | {f.rule} | '
                     f'{f.rating} | {f.reason} |')
    lines += ['', '## Geprüfte Dateien (Beleg)', '',
              f'{len(checked)} Dateien, jede einzeln gelesen.', '', '```']
    lines += [f'{path}  –  {how}' for path, how in checked]
    lines += ['```', '']
    return '\n'.join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='exit 1 if there is a Problem')
    parser.add_argument('--out', default=REPORT)
    args = parser.parse_args(argv)
    findings, checked = scan()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as f:
        f.write(report(findings, checked))
    problems = [f for f in findings if f.rating == 'Problem']
    print(f'{len(checked)} files, {len(findings)} findings, {len(problems)} problems '
          f'-> {os.path.relpath(args.out, REPO)}')
    return 1 if args.check and problems else 0


if __name__ == '__main__':
    sys.exit(main())
