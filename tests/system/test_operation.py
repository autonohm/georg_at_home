"""P8: continuous operation on the Jetson, checked without a robot and without Docker running.

- 'up real' is refused on a PC (mode file) and while the hardware scan has problems
- every long-running service of profile real restarts by itself and has a health check
- boot never starts a mission (no MISSION_ID, operating mode 'mission')
- systemd unit template and setup scripts are complete

    python -m pytest tests/system
"""

import json
import os
import shutil
import subprocess

import pytest

REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PROJECTCTL = os.path.join(REPO, 'projectctl.bash')
ONE_SHOT = {'player', 'viz', 'examples'}       # not part of continuous operation


def projectctl(*args, mode_file=None):
    env = dict(os.environ)
    if mode_file is not None:
        env['GEORG_MODE_FILE'] = str(mode_file)
    return subprocess.run(['bash', PROJECTCTL, *args], cwd=REPO, env=env,
                          capture_output=True, text=True, timeout=120)


def test_up_real_is_refused_on_a_pc(tmp_path):
    out = projectctl('up', 'real', mode_file=tmp_path / 'missing')
    assert out.returncode != 0
    assert "refused" in out.stderr and "only runs on the robot" in out.stderr
    (tmp_path / 'mode').write_text('sim\n')
    out = projectctl('up', 'real', mode_file=tmp_path / 'mode')
    assert out.returncode != 0 and 'only runs on the robot' in out.stderr


def test_up_real_is_refused_while_the_hardware_scan_has_problems(tmp_path):
    (tmp_path / 'mode').write_text('real\n')
    scan = subprocess.run(['python3', 'tools/hardware_scan.py', '--check',
                           '--out', str(tmp_path / 'report.md')], cwd=REPO)
    out = projectctl('up', 'real', mode_file=tmp_path / 'mode')
    if scan.returncode != 0:
        assert out.returncode != 0 and 'hardware scan' in out.stderr
    else:
        pytest.skip('hardware scan is clean, real would start Docker')


def test_unknown_mode_and_missing_mode_are_refused():
    assert 'unknown mode' in projectctl('up', 'party').stderr
    assert 'up needs a mode' in projectctl('up').stderr


@pytest.fixture(scope='module')
def real_services():
    if shutil.which('docker') is None:
        pytest.skip('docker CLI not installed')
    env = dict(os.environ, GEORG_PROFILE='real')
    out = subprocess.run(['docker', 'compose', '-f', 'compose.yaml', '--profile', 'real',
                          'config', '--format', 'json'], cwd=REPO, env=env,
                         capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)['services']


def test_every_service_restarts_by_itself(real_services):
    for name, service in real_services.items():
        if name in ONE_SHOT:
            continue
        assert service.get('restart') in ('unless-stopped', 'always'), name


def test_core_services_have_health_checks(real_services):
    for name in ('task_manager', 'command_gate', 'navigation', 'gestures', 'foxglove_bridge',
                 'burr_ui'):
        assert real_services[name].get('healthcheck', {}).get('test'), name


def test_boot_never_starts_a_mission(real_services):
    env = real_services['task_manager'].get('environment') or {}
    assert 'MISSION_ID' not in env
    bridge = open(os.path.join(REPO, 'packages', 'pkg_task_manager', 'georg_task_manager',
                               'georg_task_manager', 'ros_bridge.py'), encoding='utf-8').read()
    assert "self._mode = 'mission'" in bridge


def test_driver_only_in_profile_real():
    env = dict(os.environ, GEORG_PROFILE='mock')
    for profile in ('mock', 'sim', 'mcap'):
        out = subprocess.run(['docker', 'compose', '-f', 'compose.yaml', '--profile', profile,
                              'config', '--services'], cwd=REPO, env=env,
                             capture_output=True, text=True, timeout=120)
        assert 'drive' not in out.stdout.split(), profile


def test_systemd_unit_and_setup_scripts():
    unit = open(os.path.join(REPO, 'system-files', 'etc', 'systemd', 'system',
                             'georg.service'), encoding='utf-8').read()
    assert 'ExecStart=@REPO@/projectctl.bash up real' in unit
    assert 'ExecStop=@REPO@/projectctl.bash down real' in unit
    assert 'Requires=docker.service' in unit and 'WantedBy=multi-user.target' in unit
    robot = open(os.path.join(REPO, 'system-files', 'setup-robot.sh'), encoding='utf-8').read()
    pc = open(os.path.join(REPO, 'system-files', 'setup-PC.sh'), encoding='utf-8').read()
    assert 'echo real | sudo tee /etc/georg/mode' in robot
    assert 'systemctl enable georg.service' in robot
    assert 'echo sim | sudo tee /etc/georg/mode' in pc
    assert 'lichtblick' in pc.lower() and 'burr' in pc.lower()
    # installed before 'newgrp docker', which starts a new shell
    assert pc.index('/etc/georg/mode') < pc.index('newgrp docker')
    for script in ('setup-robot.sh', 'setup-PC.sh'):
        assert subprocess.run(['bash', '-n', os.path.join(REPO, 'system-files', script)]
                              ).returncode == 0
