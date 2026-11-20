# Georg Task Manager – Umbau- und Umsetzungsplan

Nov 20, 2026 · @Lenny Kossyk

## Ziel und Scope

Der Task Manager wird ein dauerhaft laufender Apache-Burr-Dienst, der ohne Roboter und ohne Simulator testbar ist. Erster Meilenstein: Eine Mission läuft im Mock-Modus zehnmal hintereinander, ist jederzeit abbrechbar und in der Burr-UI nachvollziehbar.

**Im Scope (Verantwortung Task Manager):**

- Burr-Zustandsmaschine: Idle → Mission → Idle, ohne Neustart zwischen Missionen
- ROS-Brücke: Services zum Starten und Abbrechen, Status-Topic, Action-Clients zu den Paketen
- Task-Katalog (`catalog.yaml`) als Vertrag zwischen Task Manager, Paketen und später dem LLM
- Mock-Pakete, Simulation auf dem Mac (erst einfach, dann MuJoCo), Test-Harness, Aufnahme und Replay
- Navigation (`pkg_navigation`): eigenes Paket, aber ebenfalls in Verantwortung des Task Managers
- Später: lokales LLM als Planer, das Task-Folgen und Missionsblöcke zusammenstellt und ausführen lässt

**Nicht im Scope:**

- Interne Umsetzung der Pakete Gesten und Sprache. Jedes Paket entscheidet selbst; BehaviorTree.CPP ist erwünscht, aber keine Voraussetzung.
- Neubau des Task Managers. Paketaufbau und die Art, Tasks und Missionen zu erstellen und zu starten, bleiben; nur py\_trees wird durch Burr ersetzt.
- Pause/Fortsetzen in Version 1.

## Zielarchitektur

&#91;embedded content: Zielarchitektur · Task Manager, Pakete, vier Backends\]

Input läuft über den Burr-Zustand zum LLM, der Validator lässt nur Katalog-Tasks durch, Burr führt sie über die Pakete aus. Nach jedem Task geht das Ergebnis zurück ans LLM; Lichtblick und Burr-UI zeigen alles live.

- Welches Backend aktiv ist, bestimmt allein das Compose-Profil. Burr und Pakete laufen in allen Modi unverändert.
- SLAM läuft in jedem Modus außer `mock` und erzeugt Karte und Pose für Navigation und Lichtblick.

### Bestehende Struktur bleibt: py\_trees → Burr

Paketaufbau und Workflow des Vorgängers bleiben: Tasks und Missionen werden so einfach angelegt und gestartet wie heute. Ersetzt wird nur die Ausführungs-Engine py\_trees durch Burr; wo nötig, wird die Struktur dafür angepasst. Die Zuordnung unten folgt aus den Datei- und Paketnamen und wird vor P1 gegen den Code geprüft.

| py\_trees heute | Burr künftig |
| --- | --- |
| Behaviour (z. B. Action-Client-Knoten) | Burr-Action (`@action`), ruft über die ROS-Brücke die Paket-Action |
| Sequence / Selector | Transitions mit Bedingungen (`when(...)`) |
| Blackboard | Burr-State |
| Tick-Schleife | `app.step()` / `app.run()` |
| Hilfsfunktionen in `bt_common.py` | bleiben, Burr-Actions nutzen sie weiter |
| py\_trees\_ros-Action-Clients | wandern nach `ros_bridge.py` |

### Befehls-Gate

Pakete senden Befehle immer auf dieselben Topics (`cmd_vel`, Gelenkbefehle). Was darunter hängt, bestimmt der Modus; die Pakete merken davon nichts.

| Modus | Empfänger der Befehle |
| --- | --- |
| `mock` | niemand |
| `sim` | Simulator |
| `real` | `command_gate` → Treiber |
| `mcap` | niemand |

Zwei Sicherungen:

1. Der Treiber-Container startet nur im Profil `real`.
2. `command_gate` leitet nur weiter, wenn `/etc/georg/mode` = `real` ist; sonst verwirft es alles und loggt es.

Voraussetzung: Kein Paket spricht am ROS vorbei mit der Hardware (Serial, USB, Bricklets). Nur Treiber-Nodes hinter dem Gate dürfen das. Geprüft wird das Datei für Datei im Hardware-Scan (P7), bevor echte Motoren laufen.

## Sicherheits- und LLM-Leitplanken

Das LLM ist der Planer: Es stellt Task-Folgen zusammen oder wählt ganze Missionsblöcke, und Burr führt sie ohne menschliche Freigabe aus. Sicherheit kommt aus automatischen Leitplanken um das LLM herum, nicht aus einem Menschen in der Schleife.

**Missionsblöcke** sind getestete, feste Teilabläufe, z. B. „Gast begrüßen“ = zur Tür schauen → zeigen → begrüßen. Sie stehen wie Tasks im Katalog; das LLM kombiniert Blöcke und Einzel-Tasks. Je mehr über Blöcke läuft, desto weniger kann das LLM falsch zusammensetzen.

**Ablauf einer LLM-Entscheidung:**

1. Burr baut einen kompakten Zustand: Ereignisse, Roboterzustand, Ergebnis des letzten Tasks, Anweisungen oder Feedback der Bedienperson aus Lichtblick, verfügbare Tasks und Blöcke. Keine Rohsensordaten.
2. Das LLM antwortet als JSON: eine Folge aus Tasks (`{task, args}`) und Missionsblöcken (`{block, args}`).
3. Der Validator prüft automatisch: nur Katalog-Einträge, Argumente gegen Schema, im Modus erlaubt, Vorbedingungen erfüllt, maximale Kettenlänge. Ungültiges geht mit Fehlertext zurück ans LLM; nach einer festen Zahl Korrekturversuche fällt Burr in Idle.
4. Burr führt den Plan aus. Nach jedem Task geht das Ergebnis zurück ans LLM; es entscheidet: weiter, umplanen oder abbrechen.
5. Jede Entscheidung wird gespeichert (Prompt-Version, Modell, Eingabe, Plan, Ergebnis) und ist per Entscheidungs-Replay testbar.

**Betriebsarten** (umschaltbar in Lichtblick, nach dem Start immer Mission):

| Betriebsart | Wer plant | Einsatz |
| --- | --- | --- |
| Mission | Bedienperson wählt feste Mission, kein LLM | Standard nach dem Start; Fallback, Demos, Tests |
| LLM | LLM plant und startet Missionen, Burr führt sofort aus | nur nach Aktivierung durch die Bedienperson |
| LLM + Freigabe | LLM plant, Bedienperson bestätigt den Plan in Lichtblick | optional, z. B. erste Fahrten auf dem echten Roboter |

**Harte Regeln:**

- Kein Katalog-Task sendet direkt `cmd_vel` oder Gelenkwerte. Bewegung läuft nur über Paket-Actions mit eigenen Grenzen (`twist_limiter` in `pkg_drive`).
- Abbruch wirkt immer: Cancel → laufende Paket-Action wird gecancelt → Idle.
- Not-Aus ist Hardware und unabhängig von Burr.
- In `mock`, `sim` und `mcap` existiert der Treiber-Container nicht, und das Befehls-Gate verwirft alle Motorbefehle.
- Der Modus ist an das Gerät gebunden (`/etc/georg/mode`); `projectctl.bash` verweigert `real` auf anderen Geräten.
- Autostart bringt das System nur in Idle, Betriebsart Mission. Das LLM startet Missionen nur, wenn die Bedienperson den LLM-Modus in Lichtblick aktiviert hat; der Bootvorgang selbst startet nie etwas.

## Schnittstellen

Alle Verträge liegen im neuen Paket `pkg_interfaces`; Richtung Lichtblick nur Services und Topics, Richtung Pakete Actions. Lichtblick nutzt über die Bridge Topics, Services und Parameter ([Lichtblick-Doku](https://lichtblick-suite.github.io/docs/connecting-to-data/ros2.html)); Start und Abbruch laufen deshalb als Services.

| Name | Typ | Richtung | Zweck |
| --- | --- | --- | --- |
| `/task_manager/start` | `StartMission.srv` | UI → Task Manager | Mission starten |
| `/task_manager/cancel` | `CancelMission.srv` | UI → Task Manager | Laufende Mission abbrechen |
| `/task_manager/list_missions` | `ListMissions.srv` | UI → Task Manager | Missionen für das Dropdown |
| `/task_manager/status` | `MissionStatus.msg`, QoS transient\_local | Task Manager → UI | Zustand, aktueller Task, Fehler |
| `/nav/navigate_object_x` usw. | Action je Paket | Task Manager → Paket | Task ausführen, Feedback, Cancel |

**`MissionStatus.msg`**

```
uint8 IDLE=0
uint8 RUNNING=1
uint8 SUCCEEDED=2
uint8 FAILED=3
uint8 ABORTED=4
uint8 state
string mission_id
string current_task
uint16 step
uint16 total_steps
string message
string burr_app_id   # Verweis auf den Lauf in der Burr-UI
builtin_interfaces/Time stamp
```

**`StartMission.srv`**

```
string mission_id
string params_json
---
bool accepted
string reason        # z. B. "Navigationsserver nicht erreichbar"
string burr_app_id
```

**Paket-Vertrag (jede Paket-Action):**

- Result enthält `bool success`, `string error_code`, `string message`.
- Feedback enthält `string phase`, `float32 progress`.
- Cancel wird unterstützt: Bewegung stoppt sofort, die Action meldet den Abbruch spätestens nach 2 s.
- Vorlage: `pkg_examples/pib_action_template`.

**`catalog.yaml`** – eine Zeile pro erlaubtem Task:

```yaml
tasks:
  navigate_to:
    action: /nav/navigate_object_x
    type: pkg_interfaces/action/NavigateObject
    args_schema: {target: string}
    timeout_s: 60
    cancelable: true
    modes: [mock, sim, real, mcap]
    requires: [slam_ready]
  wait_for_doorbell:
    action: /speech/wait_for_event
    type: pkg_interfaces/action/WaitForEvent
    args_schema: {event: string}
    timeout_s: 300
    cancelable: true
    modes: [mock, sim, real, mcap]
```

Action-Namen und Timeouts außer `/nav/navigate_object_x` sind Platzhalter und werden beim Umbau aus den Paketen übernommen.

## Repo-Umbau

`pkg_task_manager` enthält heute drei fremde Pakete; nach dem Umbau enthält es nur noch Burr, Katalog, ROS-Brücke und Mocks. Jedes Paket ist danach einzeln startbar und mockbar.

| Heute | Ziel | Hinweis |
| --- | --- | --- |
| `pkg_task_manager/pkg_navigation` | `packages/pkg_navigation` | eigene Dockerfile + Compose |
| `pkg_task_manager/pib_gestures_action` | `packages/pkg_gestures` | eigene Dockerfile + Compose |
| `pkg_task_manager/pib-audio` | `packages/pkg_speech` (heute leer) | eigene Dockerfile + Compose |
| `pkg_task_manager/maps` | `pkg_slam/maps` | nur Debug-Fallback, Karte entsteht per SLAM |
| `georg_task_manager/bt/task_manager_bt.py` | `burr_app/` (Migration in P1) | Struktur bleibt, nur py\_trees → Burr |
| `config/task_manager.launch.py` | auf einen Node reduzieren | heute zwei Task-Manager-Nodes |
| – | `packages/pkg_interfaces` (neu) | aus `pkg_examples/pib_action_template` ableiten |
| `pkg_viz` (RViz) | + Lichtblick, foxglove\_bridge, Panel | RViz bleibt optional |
| `pkg_object_detection` | später ROS-Node + Dockerfile | Datensatz/Modell per Git LFS oder außerhalb |

**Zielstruktur `pkg_task_manager`:**

```
pkg_task_manager/georg_task_manager/georg_task_manager/
├── ros_bridge.py        # Node, Services, Status, Action-Clients, Cancel
├── burr_app/
│   ├── builder.py       # Idle → Mission → Idle
│   ├── actions.py       # dünne Wrapper um Paket-Actions
│   └── missions/digital_festival.py
├── catalog.yaml
├── validator.py
├── mocks/               # Mock-Action-Server + Szenarien (YAML)
└── planner/             # später: LLM
```

**Modi über Compose-Profile** in einer neuen `compose.yaml` im Repo-Root, die die Paket-Compose-Dateien per `include` einbindet:

| Profil | Datenquelle | Aktoren | Treiber-Container |
| --- | --- | --- | --- |
| `mock` | keine, Pakete gemockt | keine | nein |
| `sim` | 2D-Simulator, später MuJoCo | Simulator | nein |
| `real` | echte Sensoren | `pkg_drive` | ja, nur auf dem Jetson |
| `mcap` | MCAP-Wiedergabe | keine, Pakete gemockt | nein |

Aufruf über `./projectctl.bash up <modus>`; `projectctl-completion.bash` bekommt die vier Modi.

**`system-files`:**

- `setup-robot.sh` schreibt `real` nach `/etc/georg/mode` und installiert `etc/systemd/system/georg.service`.
- `setup-PC.sh` schreibt `sim` und installiert Lichtblick und die Burr-UI.
- Die systemd-Unit startet `projectctl.bash up real` und stoppt mit `down`. Einzelne Container startet Docker mit `restart: unless-stopped` neu.

## Test- und Debug-Strategie

Der Task Manager wird fast vollständig gegen Mocks getestet; Simulator und Roboter prüfen nur noch die Integration. So hängt deine Arbeit nicht an MuJoCo oder an fertigen Paketen.

| Ebene | Was wird geprüft | Braucht | Wann |
| --- | --- | --- | --- |
| Unit | Burr-Graph, Validator, Katalog laden | nur Python (pytest) | jede Änderung |
| Mock-Integration | Task Manager + Mock-Action-Server über ROS | ROS, kein Simulator | jede Änderung |
| Entscheidungs-Replay | gespeicherten Burr-State forken, Planungsschritt N-mal ausführen, Auswahl vergleichen | Burr-Tracking-Daten, LLM | bei Prompt- oder Modelländerung |
| Simulation | Mission gegen 2D-Sim, später MuJoCo | Sim-Container | vor Merge in `main` |
| MCAP-Replay | Aufnahme → SLAM → Burr, Pakete gemockt | MCAP-Datei | vor Roboter-Tests |
| Roboter | Georg, Profil `real` | Jetson, Bedienperson | manuell |

**Mock-Szenarien** steuern, was ein gemocktes Paket zurückgibt. Damit testest du Fehlerpfade gezielt:

```yaml
# mocks/scenarios/nav_timeout.yaml
navigate_to: {result: timeout, after_s: 5}
wait_for_doorbell: {result: success, after_s: 1}
```

Pflicht-Szenarien: alles erfolgreich, ein Task schlägt fehl, Timeout, Abbruch während eines Tasks, Paket nicht erreichbar beim Start, zehn Missionen hintereinander.

**Debug-Werkzeuge:**

- **Burr-UI:** jeder Schritt mit State, Inputs und Ergebnis ([Burr UI](https://burr.apache.org/docs/ui/)).
- **Lichtblick:** Sensorik plus `/task_manager/status`.
- **Groot 2:** nur für Pakete, die intern BehaviorTree.CPP nutzen.
- **Dauer-Aufnahme:** `/task_manager/*` läuft immer als MCAP mit. `burr_app_id` verbindet Aufnahme, Status und Burr-Lauf.

**Regeln für MCAP-Replay:**

- Offene Schleife: Aufgezeichnete Odometrie reagiert nicht auf Befehle. Getestet wird Wahrnehmung → Entscheidung, nicht der Erfolg einer Fahrt.
- Nur Rohsensoren abspielen; `/map` und die TF `map→odom` nicht, wenn SLAM live läuft.
- `use_sim_time` und `/clock` setzen.
- Pro Topic genau eine Quelle.

**Determinismus des LLM:** Temperatur 0, feste Modell- und Prompt-Version. Verglichen wird die strukturierte Task-Folge, nicht der Text.

## Simulationsentscheidung

Die Simulation kommt in P3 und läuft auf dem Mac: erst ein einfacher Simulator mit denselben Topics wie Georg, dann MuJoCo. Das DeepMind-Repository hilft beim Modell, ersetzt aber nicht die ROS-Anbindung.

| Option | Liefert | Fehlt | Rolle im Plan |
| --- | --- | --- | --- |
| Mock-Action-Server (neu) | deterministische Ergebnisse, Fehlerinjektion | Physik, Sensorik | Hauptwerkzeug für Task-Manager-Tests |
| Bestehender 2D-Simulator (`simulation/`) | Odometrie, einfache Action-Ergebnisse | Lidar, Kamera, Kollision | erster Test mit echten ROS-Pfaden |
| [google-deepmind/robotics-antigravity-plugin](https://github.com/google-deepmind/robotics-antigravity-plugin) | Agent-Skills für MuJoCo (Python-API, Modell-Editing, Rendering, Studio) und Robotik-Workflows | ROS 2, Task Manager, MCAP: laut README nicht abgedeckt | hilft Claude Code, das MuJoCo-Modell von Georg zu bauen |
| [ros-controls/mujoco\_ros2\_control](https://control.ros.org/jazzy/doc/mujoco_ros2_control/doc/index.html) | ROS-2-Brücke zu MuJoCo mit Kamera, Lidar, IMU; Humble, Jazzy, Kilted | URDF-Konvertierung laut Doku „highly experimental“ | liefert die Topics, die SLAM und Navigation brauchen |

**Einordnung DeepMind-Plugin:**

- Zielplattform ist Google Antigravity. Die Skills lassen sich laut README auch einzeln per `npx skills add google-deepmind/robotics-antigravity-plugin` installieren.
- Ob die Skills in Claude Code sauber laufen, ist vor dem Einsatz zu prüfen. Einige Skills rufen Gemini-Modelle auf und brauchen `GEMINI_API_KEY`.
- Das Repository ist jung (zum Stand 2026-11-20: 2 Commits). Als Werkzeug fürs Modellbauen gut, als Fundament nicht.

**Empfehlung für den MuJoCo-Strang:** Modell aus `pkg_urdf` mit Hilfe der DeepMind-Skills nach MJCF bringen, ROS-Topics über `mujoco_ros2_control`, für die Mecanum-Basis das dortige `BaseVelocityPlugin` (fährt die Basis über ein `cmd_vel`-artiges Topic). Ergebnis: Profil `sim` liefert dieselben Topics wie `real`.

## Umsetzungsphasen

Neun Phasen (P0–P8), jede ein eigener PR mit Abnahmekriterien. Ab P2 testest du ohne Roboter, ab P3 im Simulator auf dem Mac. Echte Motoren erst nach dem Hardware-Scan in P7.

### P0 – Aufräumen und Verträge

Lieferung: Verschiebungen aus „Repo-Umbau“, `pkg_interfaces`, Root-`compose.yaml` mit Profilen, `projectctl.bash up <modus>`.

- [ ] Alle Pakete bauen mit `colcon build` ohne Fehler
- [ ] Nur noch ein Task-Manager-Node in der Launch-Datei
- [ ] `projectctl.bash up mock` startet ohne Treiber-Container
- [ ] `command_gate` vorhanden, verwirft außerhalb von `real` alles

### P1 – py\_trees-Task-Manager nach Burr migrieren

Lieferung: Paketaufbau und Workflow (Task anlegen, Mission anlegen, Mission starten) bleiben; py\_trees wird durch Burr ersetzt (Tabelle „py\_trees → Burr“). Dazu `catalog.yaml`, `validator.py`, Burr-Tracking. Zuerst gegen Fake-Funktionen, ohne ROS.

- [ ] Gleiche Mission, gleiche Reihenfolge wie im py\_trees-Stand, jetzt in Burr
- [ ] Neuen Task und neue Mission anlegen ist mindestens so einfach wie vorher; kurze Anleitung im README
- [ ] pytest: Idle → Mission → Idle, Erfolg und Fehlerpfad
- [ ] Validator lehnt unbekannte Tasks und falsche Argumente ab
- [ ] Jeder Lauf erscheint in der Burr-UI

### P2 – ROS-Brücke und Mock-Pakete

Lieferung: `ros_bridge.py` (Services, Status-Topic, Action-Clients), `mocks/` mit Szenarien, Startprüfung der benötigten Server.

- [ ] Start und Abbruch per `ros2 service call` funktionieren
- [ ] Alle Pflicht-Szenarien aus „Test- und Debug-Strategie“ laufen automatisch
- [ ] Zehn Missionen hintereinander ohne Neustart
- [ ] Fehlt ein Server, lehnt `StartMission` mit Grund ab

### P3 – Simulation auf dem Mac

Größter Schritt, in zwei Stufen. Stufe 1: einfacher Simulator, der dieselben Topics wie Georg liefert (`/odom`, `/scan`, `/tf`, Kamera optional) und `cmd_vel` annimmt. Stufe 2: MuJoCo mit `mujoco_ros2_control`, Modell aus `pkg_urdf`. Der Simulator läuft headless im Container, angezeigt wird über Lichtblick. Navigation und SLAM laufen unverändert darauf.

- [ ] `projectctl.bash up sim` startet auf dem Mac mit einem Befehl
- [ ] SLAM baut im Simulator eine Karte
- [ ] Mission mit echter Navigations-Action läuft durch
- [ ] Abbruch stoppt die Fahrt im Simulator
- [ ] `command_gate` lässt im Profil `sim` nichts an einen Treiber durch

### P4 – Lichtblick-Panel

Lieferung: Panel in `pkg_viz` mit Missionsliste, Start, Abbruch, Status, Fehlertext, `burr_app_id`.

- [ ] Bedienung komplett aus Lichtblick möglich
- [ ] Status aktualisiert sich bei jedem Burr-Schritt

### P5 – Aufnahme und Replay

Lieferung: Dauer-Aufnahme von `/task_manager/*`, Profil `mcap`, Entscheidungs-Replay-Skript in `tests/decision_replay/`.

- [ ] Gleiche MCAP-Aufnahme ergibt zweimal dieselbe Task-Folge
- [ ] Entscheidungs-Replay meldet Abweichungen als Testfehler

### P6 – LLM als Planer

Lieferung: `planner/` mit lokalem LLM, JSON-Schema für Tasks und Missionsblöcke, Rückmeldeschleife nach jedem Task, Protokoll jeder Entscheidung, Anzeige des aktuellen Plans in Lichtblick.

- [ ] Im Profil `mock` plant das LLM Missionen, Burr führt sie ohne Eingriff aus
- [ ] Ungültige Pläne gehen mit Fehlertext zurück und enden nach der Versuchsgrenze in Idle
- [ ] Schlägt ein Task fehl, plant das LLM um oder bricht sauber ab
- [ ] Entscheidungs-Replay mit festem Prompt ist stabil
- [ ] Betriebsart LLM auf `real` erst nach bestandenen Replay- und Sim-Tests

### P7 – Hardware-Scan vor dem ersten Live-Betrieb

Ziel: Sicherstellen, dass kein Paket am ROS vorbei Motoren oder andere Hardware ansteuert. Erst danach wird das Profil `real` freigegeben.

Vorgehen für Claude Code:

1. Jedes Paket unter `packages/` durchgehen, **jede Datei einzeln**: Python, C++, Launch, YAML, Dockerfile, Compose, udev-Regeln in `system-files/etc`.
2. Suchen nach direktem Hardware-Zugriff, u. a.:
   - Serial/USB: `import serial`, `serial.Serial`, `pyusb`, `/dev/tty*`, `/dev/ttyUSB`, `/dev/ttyACM`
   - Busse: `can`, `socketcan`, `smbus`, `i2c`, `spidev`
   - GPIO und Controller-SDKs: `Jetson.GPIO`, `RPi.GPIO`, `tinkerforge`, `dynamixel_sdk`
   - Compose/Docker: `devices:`, `privileged: true`, Volumes auf `/dev`
3. Jeden Fund bewerten: Treiber-Paket (erlaubt) oder anderes Paket (Problem).
4. Funde in anderen Paketen nicht selbst umbauen, sondern dem Paket-Verantwortlichen melden.
5. Ergebnis in `docs/hardware_access_report.md`: Paket · Datei · Zeile · Fundstelle · Bewertung, dazu die Liste aller geprüften Dateien als Beleg.

- [ ] Jede Datei in jedem Paket geprüft und im Report gelistet
- [ ] Hardware-Zugriff nur noch in Treiber-Paketen hinter dem `command_gate`
- [ ] Offene Funde gemeldet und behoben
- [ ] Profil `real` erst danach freigegeben

### P8 – Dauerbetrieb auf dem Jetson

Lieferung: `georg.service`, `/etc/georg/mode`, Healthchecks, `restart: unless-stopped`.

- [ ] Nach dem Einschalten steht Georg in Idle
- [ ] Ein abgestürzter Container kommt allein wieder hoch
- [ ] `up real` wird auf dem PC verweigert

### Hinweis zu MuJoCo

MuJoCo ist Stufe 2 von P3. Die DeepMind-Skills helfen beim Modell, die ROS-Anbindung kommt aus `mujoco_ros2_control` (siehe „Simulationsentscheidung“).

## Arbeitsregeln für Claude Code

Claude Code bearbeitet genau eine Phase pro Sitzung und stoppt nach den Abnahmekriterien. Diese Doku liegt als `docs/task_manager_plan.md` im Repo (Export als Markdown).

1. Branch `refactor/task-manager-burr`, ein PR pro Phase.
2. Zuerst lesen: `README.md`, `projectctl.bash`, `packages/pkg_task_manager/`, `packages/pkg_examples/`, `system-files/README.md`.
3. Verschieben nur mit `git mv`, damit die Historie erhalten bleibt.
4. In fremden Paketen nur Pfade, Imports, Dockerfiles und Compose ändern, keine Logik.
5. Nichts löschen ohne Rückfrage. Freigegeben ist nur der doppelte Node in der Launch-Datei. Bestehende Struktur erhalten: umbauen, nicht neu schreiben.
6. Nie das Profil `real` starten, keine Befehle an Hardware senden. Das Profil real wird erst nach dem Hardware-Scan (P7) freigegeben.
7. Jede Phase endet mit grünem `colcon build`, `colcon test` und pytest.
8. Unklarheiten nicht raten, sondern in `docs/OPEN_QUESTIONS.md` notieren und nachfragen.
9. Keine Secrets oder API-Keys committen.

**Start-Prompt für Claude Code:**

```
Lies docs/task_manager_plan.md vollständig. Setze nur Phase P0 um.
Halte dich an „Arbeitsregeln für Claude Code“. Zeig mir vor dem ersten
Verschieben die Liste aller betroffenen Dateien und Imports.
Stoppe, wenn alle Abnahmekriterien von P0 erfüllt sind.
```

## Entscheidungen und offene Fragen

| Thema | Entscheidung | Folge |
| --- | --- | --- |
| ROS-2-Distribution | Jazzy | `mujoco_ros2_control` per apt (`ros-jazzy-mujoco-ros2-control`) |
| LLM-Hardware | Jetson Thor, auf dem Roboter | LLM als eigener Dienst mit HTTP-Endpunkt; der Planer kennt nur den Endpunkt, Modell und Hardware bleiben austauschbar |
| Burr-Laufzeit | Empfehlung: venv mit `--system-site-packages` im Task-Manager-Container | rclpy aus Jazzy bleibt sichtbar, Burr-Version sauber gepinnt |
| Bridge | Empfehlung: foxglove\_bridge | schnell bei Kamera und Lidar; Start/Abbruch als Services |
| Cancel | Bewegung stoppt sofort; Action meldet Abbruch spätestens nach 2 s | Pflicht-Szenario in Mock- und Sim-Tests |

- [ ] Wer verantwortet Gesten, Sprache und den MuJoCo-Strang? (Team-Absprache)
- [ ] Welche Lichtblick-Version setzt ihr ein? Für das Panel festpinnen.
- [ ] Pause für Version 2: Variante A (Task abbrechen, Plan-Position merken, Task neu starten) oder B (echtes Pausieren in jedem Paket)? Empfehlung A.

## Quellen

- [Apache Burr: State Persistence und Forking](https://burr.apache.org/concepts/state-persistence/)
- [Apache Burr: UI](https://burr.apache.org/docs/ui/)
- [google-deepmind/robotics-antigravity-plugin](https://github.com/google-deepmind/robotics-antigravity-plugin)
- [mujoco\_ros2\_control Dokumentation](https://control.ros.org/jazzy/doc/mujoco_ros2_control/doc/index.html)
- [mujoco\_ros2\_control\_plugins (u. a. BaseVelocityPlugin)](https://docs.ros.org/en/humble/p/mujoco_ros2_control_plugins/index.html)
