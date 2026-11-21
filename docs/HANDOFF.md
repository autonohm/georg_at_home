# Übergabe: Stand und nächste Schritte

Stand 2026-11-21, Branch `pkg_task_manager_burr`. Für die nächste Arbeitssitzung (Mensch oder
Claude Code). Gearbeitet wird jetzt auf dem **Jetson Thor (nicht am Roboter angeschlossen)**. **Zuerst diese Datei lesen**, dann
`docs/task_manager_plan.md` (Plan P0–P8), `docs/OPEN_QUESTIONS.md`, `docs/P8_ANLEITUNG.md`.

## Arbeitsregeln (gelten weiter)

- **Nie das Profil `real` starten, keine Befehle an Hardware senden.** Nur `mock`, `sim`, `mcap`.
- Dateien nur mit `git mv` verschieben. Nichts löschen ohne Rückfrage.
- Fremde Pakete (Navigation, Gesten, SLAM, …): nur Pfade, Imports, Dockerfiles, Compose anpassen,
  Funde in `docs/OPEN_QUESTIONS.md` melden statt umbauen. Ordner fremder Pakete nicht umbenennen.
- Keine Geheimnisse/API-Keys committen. Push nur nach Rückfrage.
- `main` wird nie direkt geändert; `main` nur in unseren Branch mergen.
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

## Gesamtplan (vereinbart 2026-11-21)

0. **Gate entfernt, `ROS_DOMAIN_ID` pro Profil – erledigt** (Q32): `real` 0, alle anderen
   `GEORG_SIM_DOMAIN_ID` (Default 30).
1. **Merge `main` → unser Branch – erledigt.** Sams `sim_mode` übernommen (in `real` aktiv,
   `sim`/`mcap` vorerst eigene Launch-Dateien, Q30). Kein Robot-Namespace mehr, alles folgt
   `EDU_ROBOT_NAMESPACE` (Default leer): Services heißen `/task_manager/start` usw.
2. **Docker auf dem Jetson.** Basis-Image auf arm64 (`docker_base_image/compose.yaml` baut nur
   amd64). Alte Container `georg-drive-1`/`georg-urdf-1` (Stand von vor 2 Wochen aus
   `software/`, gleicher Projektname `georg`, gleiches Netz) erst stoppen, alte Images taggen.
   Dann `build`, `up mock`, `up sim`, Healthchecks, `tests/system`, alle ROS-Tests im Container,
   Lichtblick verbinden. Ergebnis in `OPEN_QUESTIONS.md`.
3. **Georg komplett in Lichtblick.** Eigenes Paket (z. B. `pkg_pib_model`), `pkg_urdf` bleibt
   unangetastet:
   - Konverter `model.json` (Cerebra-Robotermodell aus pib-backend, `/data/robot-model` im
     Container `pib-backend-flask-app-1`, oder `/api/robot-model/...`) → `pib.urdf`. Das Format
     ist schon ein URDF als JSON (47 Links mit GLB, 48 Gelenke mit origin/axis/limit).
   - An `georg_description` hängen (`pib_waist_link` → `root`), in Lichtblick abgleichen.
   - Meshes verkleinern (1,58 Mio. Dreiecke, 36 MB), beim Build/Start holen statt ins Repo
     kopieren (Lizenz ungeprüft, Modellversion zieht mit).
   - Joint-State-Umsetzer: pib-backend `/joint_states` (Motornamen, Centigrad) → URDF-Gelenke
     (Radiant) nach `mapping.json` (Richtung, Offset, gekoppelte Finger).
   - Sim: Fake-Motors-Node (`/apply_joint_trajectory`, `/joint_trajectory` → `/joint_states`),
     damit Gesten sichtbar werden. Isaac Sim ist verworfen (läuft nicht auf Jetson).
4. **Fahren in MuJoCo realistischer.** Basis-Mesh, Räder, zwei Lidare an den URDF-Positionen
   mit Rauschen → `merged_scan`, Odometrie-Drift und Latenz als Parameter. Simulator sendet
   `/clock` und `odom/wheel`, dann `sim_mode` auch im Profil `sim` (Q30). Planer-Inflation
   0,25 m → ca. 0,32 m an die Navigation melden.
5. **pib-backend und Sprache – vereinbart, aber erst auf Ansage.** Branch
   `origin/pib_backend_integration` (alter `software/`-Stand) nicht mergen, sondern portieren:
   `Speak` (`/play_audio_from_speech`), `wait_for_service_result`, Mission „Greeting“.
   Externes Netz `pib-network`. Namenskonflikt `datatypes`: unser Paket (Listen/VoiceEvent/
   VoiceTask) fällt weg, das von pib-backend wird genutzt (hat keine `Listen`-Action),
   Listening neu auf `/speech_detected` bzw. `/chat` (löst Q1).
6. **Gesamttest** in `sim`: Fahren, Gesten, (ab 5) Sprache; Abnahmelisten P2–P8 im Container;
   instabilen MuJoCo-Test klären.
7. **Roboter (später, nur mit Mensch am Roboter):** 12 Hardware-Scan-Funde mit den Teams,
   `edu_robot` und `cmd_vel` prüfen, Q31 (Navigation liest `odom`), dann erster `real`-Test.

### Frühere nächste Schritte

Kamerabild in der Sim (Topic/Auflösung/Einbauposition der Luxonis-Kamera offen), Arena als Welt
(`packages/pkg_sim/assets/arena/`), pylint-Aufräumen (nicht freigegeben) – nach Phase 6.

## Offene Punkte (Auszug, Details in `docs/OPEN_QUESTIONS.md`)

- Wer liefert auf dem Roboter den `audio/listen`-Server (seit `pib-audio` weg ist)? (Q1)
- Hardware-Scan: 12 Probleme in fremden Paketen → Profil `real` gesperrt
  (`docs/hardware_access_report.md`, `tools/hardware_scan.py`).
- Planer-Inflation 0,25 m ist zu klein für Georgs Basis (0,49 × 0,40 m, halbe Diagonale ≈ 0,32 m).
- Git LFS für die Arena-Dateien: Entscheidung offen.
- `georg_sim` hält die Ordnerregel (`<paket>_pkg`) noch nicht ein.
- Q30 (sim_mode vs. Simulator-Odometrie), Q31 (Navigation liest `odom`), fremde RViz-Konfigurationen mit `/georg/...`.
