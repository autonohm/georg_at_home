# Übergabe: Stand und nächste Schritte

Stand 2026-11-21, Branch `pkg_task_manager_burr`. Für die nächste Arbeitssitzung (Mensch oder
Claude Code), z.B. per SSH auf dem Windows-PC. **Zuerst diese Datei lesen**, dann
`docs/task_manager_plan.md` (Plan P0–P8), `docs/OPEN_QUESTIONS.md`, `docs/P8_ANLEITUNG.md`.

## Arbeitsregeln (gelten weiter)

- **Nie das Profil `real` starten, keine Befehle an Hardware senden.** Nur `mock`, `sim`, `mcap`.
- Dateien nur mit `git mv` verschieben. Nichts löschen ohne Rückfrage.
- Fremde Pakete (Navigation, Gesten, SLAM, …): nur Pfade, Imports, Dockerfiles, Compose anpassen,
  Funde in `docs/OPEN_QUESTIONS.md` melden statt umbauen. Ordner fremder Pakete nicht umbenennen.
- Keine Geheimnisse/API-Keys committen. Push nur nach Rückfrage.
- Antworten auf Deutsch. Commit-Nachrichten enden mit
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## Was fertig ist

- Plan P0–P8 umgesetzt und auf dem Mac getestet (Details: `docs/P8_ANLEITUNG.md`).
- Task Manager: Burr-Engine, Services start/cancel/list/set_mode/instruct/approve_plan,
  Status-Topic, Katalog + Validator, LLM-Planer (OpenAI-kompatibel, `pkg_llm`), Mock-Pakete,
  MCAP-Aufnahme/Replay, Decision-Replay, Lichtblick-Panel.
- Paketstruktur (Regel in der Haupt-README „Aufbau eines Subsystems“):
  `packages/pkg_task_manager/task_manager_pkg/task_manager/` – ROS-Paket und Python-Modul
  heißen `task_manager`, Nachrichten `georg_task_manager_msgs`.
- `pib-audio` entfernt, `datatypes` (Listen-Action) liegt in `pkg_interfaces`.
- Simulation: `georg_sim` (sim2d, simmj mit MuJoCo), SLAM, echte Navigation, Command Gate,
  foxglove_bridge. Georgs Modell (`georg_description`, Commit `2586a94`) wird in Lichtblick
  angezeigt; MuJoCo-Fenster optional.

### Tests (zuletzt grün auf dem Mac)

Unit 62+4+7, Replay/System 13, ROS/Mock 10, Sim2d 5, MuJoCo 5, Lichtblick 4, MCAP 4+5, LLM 9.

## Starten

**Mac (ohne Docker, pixi):** `cd dev/macos`, dann
`pixi run fetch_description && pixi run build`, danach
`pixi run sim_mj` (oder `sim_mj_view` mit MuJoCo-Fenster) und `pixi run -e ui burr_ui`.
Lichtblick: `ws://localhost:8765`, Layout `packages/pkg_viz/lichtblick_layouts/georg_sim.json`.
Tests: `pixi run test`, `test_ros`, `test_sim`, `test_sim_mj`, `test_lichtblick`, `test_mcap`,
`test_llm`.

**Linux/WSL (Docker, so wie auf dem Roboter):** im Repo-Root
`./projectctl.bash build`, dann `./projectctl.bash up mock` bzw. `up sim`,
`./projectctl.bash status`, `./projectctl.bash down`. Lichtblick vom Mac: `ws://<PC>:8765`.

## Nächste Schritte

1. **Docker-Test auf dem Windows-PC** (noch nie gebaut/gestartet, wichtigster offener Punkt).
   - PC: Windows, WSL2 `Ubuntu-22.04`, Docker Desktop **4.15 – zu alt**: `compose.yaml` nutzt
     `include:` (braucht Docker Compose ≥ 2.20, Docker Desktop ≥ 4.22). Erst aktualisieren,
     WSL-Integration für Ubuntu-22.04 einschalten.
   - Erreichbar über Tailscale: `desktop-l`, `100.109.75.119`, Benutzer `Thales`.
     OpenSSH-Server war am 2026-11-21 noch nicht installiert.
   - PC ist amd64, der Jetson arm64: der Test prüft Dockerfiles/Compose/Netz, nicht ARM.
   - Ablauf: im WSL-Ubuntu klonen, `./projectctl.bash build`, `up mock`, `up sim`,
     Healthchecks (`status`), `tests/system`, Lichtblick vom Mac verbinden, `down`.
     Fehler beheben, Ergebnis in `docs/OPEN_QUESTIONS.md` (Docker-Verifikation) eintragen.
2. **Georg in MuJoCo (Schritt a, begonnen, noch nicht umgesetzt):** URDF aus `georg_description`
   in die MJCF-Welt (`pkg_sim/georg_sim/georg_sim/mjcf.py`) übernehmen. Meshes nur visuell
   (STL/OBJ; DAE der Lidare kann MuJoCo nicht → Zylinder), Kollision einfache Form.
   Dabei realistischer machen: zwei Lidare an den URDF-Positionen (laser1/laser2) mit Rauschen,
   zusammengeführt zu `merged_scan`; Rauschen/Drift der Odometrie und Latenz als Parameter.
3. **Kamerabild in der Sim:** MuJoCo offscreen rendern, `sensor_msgs/Image` + `CameraInfo` auf
   demselben Topic/Frame wie die echte Luxonis-Kamera. **Offen:** Topic, Auflösung, Bildrate und
   Einbauposition der echten Kamera (vom Team erfragen).
4. **Arena als Welt (Schritt b):** `packages/pkg_sim/assets/arena/` (nicht in git, siehe dortige
   README): Blender-Export, vereinfachen, Kollision als Quader, daraus auch die Nav-Karte (YAML)
   erzeugen, neue Zielorte für Missionen.
5. **pylint-Aufräumen** (Vorschlag, noch nicht freigegeben): `.pylintrc` (Zeilenlänge 99,
   Import-Reihenfolge aus wegen flake8), Docstrings, `encoding='utf-8'`, `check=` bei
   `subprocess.run`. Score Paket 9.20, Tests 8.49.

## Offene Punkte (Auszug, Details in `docs/OPEN_QUESTIONS.md`)

- Wer liefert auf dem Roboter den `audio/listen`-Server (seit `pib-audio` weg ist)? (Q1)
- Hardware-Scan: 13 Probleme in fremden Paketen → Profil `real` gesperrt
  (`docs/hardware_access_report.md`, `tools/hardware_scan.py`).
- Planer-Inflation 0,25 m ist zu klein für Georgs Basis (0,49 × 0,40 m, halbe Diagonale ≈ 0,32 m).
- Git LFS für die Arena-Dateien: Entscheidung offen.
- `georg_sim` und `command_gate` halten die Ordnerregel (`<paket>_pkg`) noch nicht ein.
