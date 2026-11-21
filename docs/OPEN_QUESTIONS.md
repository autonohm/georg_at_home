# Offene Fragen – P0

Stand: 2026-11-20. Gemäß Arbeitsregel 8 notiert, nicht geraten.

## Entschieden

| # | Thema | Entscheidung (2026-11-20) | Umgesetzt |
| --- | --- | --- | --- |
| Q2 | Welcher Task-Manager-Node bleibt | Variante A: nur der sequenzielle `task_manager`. `task_manager_bt` (py_trees) bleibt im Code, wird nicht mehr gestartet und in P1 durch Burr ersetzt. | ja |
| Q3a | Doppeltes Paket `drive_route_server` | Ältere Kopie `drive_route_server_pkg/drive_route_pkg/` gelöscht. | ja |
| Q3b | Verschachtelte Task-Manager-Kopie | Gelöscht. Vorher gerettet: `tasks/Navigate.py`, `tasks/GraspPlanning.py`, `missions/Comparison.py`, `missions/ComparisonNav.py` (wurden von py_trees-Code importiert). | ja |
| Q4 | Interfaces | Alle nach `packages/pkg_interfaces`, Paketnamen bleiben, ins Basis-Image gebaut. Gesten-Action heißt jetzt `georg_gesture_msgs`. | ja, außer `datatypes` (Q1) |
| Q8 | Gitlink `pib_sdk` | Gitlink entfernt, `pib-sdk==0.9.1` per pip im Gesten-Dockerfile. | ja |
| Q9 | Branch | `pkg_task_manager_burr` bleibt. | – |

Nebenbei entfernt: 13 eingecheckte `.pyc`-Dateien in der Navigation (Kompilate, kein Quellcode).

## Offen

**Q1 – `pkg_speech` zurückgestellt.** Ihr arbeitet gerade daran. `pib-audio` bleibt deshalb vorerst in `pkg_task_manager`, samt `datatypes` (Listen-Action) und Voice-Node im Task-Manager-Launch. Sobald der Stand klar ist: nach `pkg_speech` verschieben und `datatypes` nach `pkg_interfaces`.
**Stand 2026-11-21:** `pib-audio` gelöscht (Entscheidung Team). `datatypes` liegt jetzt in `packages/pkg_interfaces/datatypes` (Basis-Image). Der Task-Manager-Container startet keinen `listen_action_server` mehr und hat keine Audio-Pakete und kein `/dev/snd` mehr. **Offen:** Wer liefert auf dem Roboter den Server `audio/listen` (z.B. pib-backend-Fork)? Bis dahin schlägt der Listening-Task im Profil `real` fehl; mock/sim nutzen die Mock-Pakete.

**Q4b – `navigate_server.grid_rasterizer` im Task Manager.** `NavigateObject`/`NavigateRoom` lesen die Karte selbst. Übergangslösung: `navigate_server` wird im Task-Manager-Container mitgebaut (zusätzlicher Build-Kontext). Vorschlag für P1: Task Manager schickt nur den Objektnamen, die Navigation löst ihn auf.

**Q5 – erledigt durch Umbau.** Ungültige Abhängigkeiten `georg_msgs`, `georg_nav_action`, `pib-audio` in `task_manager_pkg/package.xml` ersetzt durch `georg_gesture_msgs`, `datatypes`, `georg_nav_msgs`. Bitte kurz bestätigen.

**Q6 – `privileged: true` und `/dev`-Mounts** in Task Manager, SLAM, Viz, Drive. Unverändert gelassen, Bewertung im Hardware-Scan P7.

**Q7 – Befehls-Gate: Abweichung vom Plan.** Umgesetzt als `packages/pkg_command_gate`: `cmd_vel` → Gate → `cmd_vel/gated` → Treiber. Der Treiber in `pkg_drive/config/drive.launch.py` hört jetzt per Remap auf `cmd_vel/gated`. Ungeprüft: ob `edu_robot` wirklich `cmd_vel` abonniert, sonst greift der Remap nicht (Prüfung in P7). Abweichung: Auf dem Mac gibt es kein `/etc/georg`, ein Bind-Mount würde dort scheitern. Deshalb liest `projectctl.bash` die Datei auf dem Host und übergibt sie als `GEORG_DEVICE_MODE`; zusätzlich muss das gestartete Profil `real` sein. Offen: Gelenkbefehle der Gesten laufen nicht über das Gate. Welches Topic?

**Q10 – Maps.** Liegen jetzt in `pkg_slam/maps` und werden in Navigation und Task Manager unter `/root/georg_maps` eingebunden. Feste Pfade in den Missionen unverändert. BT-Missionen und `drive_route_server` erwarten `Nav_Test_V3.yaml`, die es nicht gibt.

**Q11 – Bauen. TEILWEISE ERLEDIGT (2026-11-20).** Auf dem Mac läuft ROS 2 Jazzy jetzt über RoboStack und pixi (`dev/macos/`). Damit sind geprüft: `colcon build` aller 13 ROS-Pakete in `packages/` ohne Fehler, 99 Task-Manager-Tests und 4 Gate-Tests mit echtem ROS, ein Probelauf des Befehls-Gates (verwirft in `sim`) und ein Probelauf des echten Task-Manager-Nodes mit Burr. Noch offen: der Build der Docker-Images und `./projectctl.bash up mock`. Das geht erst auf einem Rechner mit laufendem Docker (Windows-PC oder Jetson, auf dem Jetson nur `build`, kein `up real`).

## Neu gefunden (bestehende Fehler, nicht behoben)

**Q12 – Action-Namen passen nicht.** Der Launch startet den Navigationsserver unter `/nav/navigate` (absolut). Der Task Manager ruft `nav/navigate_object_x` und `nav/navigate_room_x` im Namespace `georg` auf. Ein Server bedient nur einen Namen. In `pkg_navigation/config/navigation.launch.py` unverändert übernommen und mit TODO markiert. Welche Namen sollen gelten?

**Q13 – Navigation umgeht `twist_limiter`.** `drive_route_server` sendet direkt auf `cmd_vel`, nicht auf `cmd_vel/nav` (Eingang von `twist_mux`). Damit greifen weder `twist_mux` noch `twist_limiter`. Das verstößt gegen die harte Regel „Bewegung nur über Paket-Actions mit eigenen Grenzen“. Das Gate fängt den Weg außerhalb von `real` ab, auf dem Roboter aber nicht. Fix ist eine Zeile in der Navigation, also Logik: freigeben?

**Q14 – Gesten-Result entspricht nicht dem Paket-Vertrag.** `PibGesturesInterface` liefert `int8 success` statt `bool success`, `string error_code`, `string message`. Feedback ist `string status` statt `phase` und `progress`. Unverändert, Anpassung mit dem Gesten-Verantwortlichen.

**Q15 – Kleinkram.** `navigate_server` registriert `fake_odom` aus `odom_sim.py`, die Datei fehlt (gab es nur noch als `.pyc`). `docker_base_image/compose.yaml` taggt `georg-ros:humble`, alles andere nutzt `jazzy`. `projectctl.bash install_completion` zeigte auf `packages/projectctl-completion.bash`, korrigiert auf `system-files/`.

# Offene Fragen – P1

**Q16 – py_trees-Code löschen?** Burr ersetzt die Ausführung, `main.py` nutzt jetzt `BurrTaskManager`. Noch im Repo, aber ungenutzt: `bt/`, `tasks_bt/`, die Entry-Points `task_manager_bt` und `render_mission_bt` in `setup.py`, die apt-Pakete `ros-jazzy-py-trees*` im Dockerfile und die Abhängigkeiten in `package.xml`. Ebenso die alte Schleife `task_manager.py`; sie dient in `test_burr_app.py` als Referenz für die gleiche Reihenfolge. Löschen erst nach deiner Freigabe (Regel 5).
**Erledigt (2026-11-21):** py_trees-Code gelöscht (P1), `task_manager.py`, `main.py`, `ros_adapter.py`, `demo_burr.py`, `Navigate.py`, `GraspPlanning.py`, `Comparison*.py` und der Vergleichstest gelöscht; Modul umbenannt (`burr_app`→`engine`, `ros_bridge.py`→`node.py`, `Georg.py`→`robot.py`, `interface.py`→`state.py`, Katalog nach `catalog/`, `mission_selector.py`→`missions/__init__.py`).

**Q17 – Abweichung von der Zielstruktur.** Der Plan nennt `burr_app/missions/digital_festival.py`. Die Missionen bleiben in `missions/`, weil der Plan auch sagt, dass Tasks und Missionen so angelegt werden wie bisher. Ein zweiter Ort für Missionen würde das verdoppeln.

**Q18 – Ein Burr-Lauf pro Mission.** Jede Mission bekommt eine eigene `burr_app_id`, der Dienst selbst bleibt zwischen Missionen im Leerlauf. So erscheint jeder Lauf einzeln in der Burr-UI, und `StartMission` kann die ID zurückgeben. Die Alternative wäre eine durchgehende Burr-App für alle Missionen.

**Q19 – flake8 im Task Manager war schon vorher rot.** Der bestehende Code hat 203 flake8-Meldungen, `colcon test` scheitert dort also unabhängig von P1. Der neue Code (`burr_app/`, `catalog.py`, `validator.py`, Tests, `command_gate`) ist sauber. Bestehenden Code formatieren, oder flake8 für Altdateien ausnehmen?

**Q20 – Noch nicht im Container gelaufen.** 93 Tests laufen lokal ohne ROS grün (Python 3.9, Burr 0.43.0). Die Burr-UI hat einen lokalen Lauf angezeigt. Im Container (Python 3.12, echtes rclpy) ist das noch ungeprüft, genauso wie der Build aus P0.

# Entscheidung – Darstellung in Burr (2026-11-20)

**Entschieden: Mischung aus Kette (A) und Stern (B).** Burr bleibt die Ausführung.

| Betrieb | Graph | Was man sieht |
| --- | --- | --- |
| Feste Mission, Missionsblock | **Kette (A):** ein Knoten pro Missionsschritt, beim Start gebaut | Plan, Abbruchstelle und Rest auf einen Blick |
| LLM-Betrieb (P6) | **Stern (B):** `next` plus ein Knoten pro Katalog-Task und pro Missionsblock | Reihenfolge in der Schrittliste; `next` zeigt Entscheidung und Absicht des LLM |
| Block im LLM-Betrieb | Block-Knoten startet einen Unter-Lauf mit Kette (A) | Block als aufklappbare Kette unter dem Schritt |

Begründung: Burr baut den Graphen vor dem Lauf. Eine Kette geht nur, wenn der Plan vorher feststeht (Mission, Block). Das LLM entscheidet unterwegs, dafür ist der Stern das Burr-Standardmuster. Der Stern wächst mit dem Katalog, nicht mit der Laufzeit (erwartet 10 bis 20 Knoten).

Verworfen:
- **C, ein Unter-Lauf pro LLM-Abschnitt:** Bei häufigem Umplanen entsteht fast pro Schritt ein Lauf, der Durchlauf ist auf viele Teile verteilt.
- **D, Graph während des Laufs nachzeichnen:** Wird von Burr nicht unterstützt.
- **F, versteckte Pfad-Hervorhebung der Burr-UI einschalten:** Sonderlösung in fremdem Code.
- **Langfuse:** sechs Container, etwa 16 GB RAM.
- **Phoenix:** Reserve, falls der Stern im LLM-Betrieb nicht reicht.

Der Code für den Stern liegt im Commit `6c3f685` und wird in P6 wieder eingebaut.

**Q21 – Mission gilt als erfolgreich, obwohl kein Task geklappt hat.** Probelauf auf dem Mac ohne Paket-Server: Alle Tasks scheitern, trotzdem endet die Digital-Festival-Mission mit „succeeded“. Grund sind die bestehenden Prioritätsregeln: Low und High werden nach dem Scheitern verworfen, und die Mission läuft weiter. Nur Critical bricht ab. Sollen wichtige Tasks wie die Klingel Critical werden, oder soll eine Mission mit verworfenen Tasks einen eigenen Ausgang bekommen, etwa „teilweise“?

# P2 – Stand (2026-11-20)

Auf dem Mac (RoboStack) umgesetzt und geprüft:

| Abnahmekriterium P2 | Stand |
| --- | --- |
| Start und Abbruch per `ros2 service call` | erfüllt |
| Alle Pflicht-Szenarien laufen automatisch | erfüllt: `test/test_ros_integration.py`, 10 Tests, zweimal hintereinander grün |
| Zehn Missionen hintereinander ohne Neustart | erfüllt, gleicher Prozess |
| Fehlt ein Server, lehnt `StartMission` mit Grund ab | erfüllt, Grund nennt die Action |

**Q22 – Neuer Code im ROS-Stil.** Der neue Code (Burr, Katalog, Validator, Brücke, Mocks, Tests, Gate) ist auf den ROS-Stil umgestellt: einfache Anführungszeichen, Google-Importreihenfolge. `ament_flake8` meldet dafür keine Probleme. Der Altbestand des Task Managers ist weiter rot (Q19), deshalb ist `colcon test` für dieses Paket noch nicht grün.

**Q23 – `MISSION_ID` entfernt.** Der Node `task_manager` ist jetzt die Brücke und startet nach dem Booten nichts. Die alte Variante `task_manager_cli` ist seit 2026-11-21 gelöscht. Im Compose ist `MISSION_ID` entfernt.

**Q24 – Paket-Vertrag noch nicht umgesetzt.** Die echten Actions haben noch nicht das vereinbarte Ergebnis (`success`, `error_code`, `message`) und Feedback (`phase`, `progress`). Die Mocks bilden die heutigen Actions nach. Die Anpassung betrifft die Pakete selbst, siehe Q14.

# P3 – Stand (2026-11-20)

Auf dem Mac (RoboStack) umgesetzt und geprüft, Stufe 1 (2D-Simulator `georg_sim/sim2d`):

| Abnahmekriterium P3 | Stand |
| --- | --- |
| `up sim` startet auf dem Mac mit einem Befehl | ohne Docker: `pixi run sim` startet alles; `./projectctl.bash up sim` ungeprüft (Docker) |
| SLAM baut im Simulator eine Karte | erfüllt (`/map`) |
| Mission mit echter Navigations-Action läuft durch | erfüllt (`sim_seat`, Roboter erreicht den Sitzplatz) |
| Abbruch stoppt die Fahrt | erfüllt (Roboter steht nach Abbruch still) |
| `command_gate` lässt in `sim` nichts durch | erfüllt |

**Entscheidungen (ohne Rückfrage, Auftrag vom 2026-11-20):**
- **Q12 erledigt:** Navigation startet zwei Planungsserver unter `nav/navigate_object_x` und `nav/navigate_room_x` (Namen aus `Georg.py`).
- **Kartenname beim Fahren:** `NavigateObject` und `NavigateRoom` geben die Karte jetzt an den Fahrserver weiter (`drive_goal.map_name`). Ohne das hielt er jede bekannte Wand für ein Hindernis, weil seine Ersatzkarte `Nav_Test_V3.yaml` fehlt. `Navigate.py` machte es schon so.
- **Mock-Odometrie abschaltbar:** Szenario `odom: false`, sonst stören zwei Odometrie-Quellen die Navigation.
- **SLAM-Karte liegt auf `/map`** (slam_toolbox veröffentlicht absolut, nicht im Namespace).
- **Simulator-Radius 0,2 m:** Der Planer hält 0,25 m Abstand zu Wänden. Ist Georg breiter als 0,5 m, ist dieser Abstand zu klein (Hinweis an die Navigation).

**Q25 – Engstellen in `Nav_Test.yaml`.** Der Weg zum Sitzplatz führt durch Lücken von etwa 0,55 m (zwischen `Wall2` und `Wall3`). Für einen echten Roboter mit 0,5 m Durchmesser ist das sehr knapp.

**P3 Stufe 2 – MuJoCo (2026-11-20).** `georg_sim/simmj`: dieselben Topics wie `sim2d`, Physik und Laser aus MuJoCo 3.16. Das Modell wird aus der Karten-YAML gebaut (`mjcf.py`): Wände als Quader, Basis als Zylinder mit Geschwindigkeits-Aktoren für x, y und Gier. Die komplette P3-Abnahme läuft auch mit MuJoCo grün (`pixi run test_sim_mj`).
- **Abweichung vom Plan:** `mujoco_ros2_control` gibt es für macOS nicht (RoboStack, Stand 2026-11-20). Die Node spricht deshalb direkt mit MuJoCo. Auf Linux kann das Modell später über `mujoco_ros2_control` laufen, die Topics bleiben gleich.
- **Offen (Q26):** Das echte Robotermodell aus `pkg_urdf` (externes Repo `georg_description`) ist noch nicht übernommen. Die Basis ist ein Zylinder mit 0,2 m Radius. Die DeepMind-Skills wurden nicht eingesetzt; sie brauchen teils einen Gemini-API-Schlüssel und Antigravity.

# P4 – Stand (2026-11-20)

| Abnahmekriterium P4 | Stand |
| --- | --- |
| Bedienung komplett aus Lichtblick möglich | über `foxglove_bridge` automatisch geprüft (Missionsliste, Start, Abbruch, Ablehnungsgrund, Status), mit demselben WebSocket-Protokoll wie Lichtblick; das Panel selbst mit simuliertem DOM und Lichtblick-Kontext. **Nicht** geprüft: das Panel in einem echten Lichtblick-Fenster. |
| Status aktualisiert sich bei jedem Burr-Schritt | erfüllt, jeder Schritt kommt über die Brücke an (dreimal hintereinander grün) |

**Entscheidungen:**
- **Lichtblick-Version festgelegt: 1.30.0** (2026-10-22). 1.31.0 war erst vier Tage alt.
- **Panel ohne npm**, reines JavaScript, Paket mit `build.py`. Grund: Der automatische Freigabe-Filter hat `npx create-lichtblick-extension` (Code aus dem Netz ausführen) blockiert. Wer das Panel später mit React/TypeScript neu aufsetzen will, kann `src/model.js` übernehmen.
- **`foxglove_bridge` 3.x spricht nur `foxglove.sdk.v1`**, Lichtblick 1.30 bietet es an. Ältere Lichtblick-Versionen mit nur `foxglove.websocket.v1` können sich nicht verbinden.
- **`min_qos_depth:=10` für die Brücke**, Status-Publisher mit Tiefe 10: Sonst gingen die letzten, schnell aufeinanderfolgenden Burr-Schritte verloren.
- Brücke als Dienst `foxglove_bridge` in `pkg_viz`, Port 8765, in allen vier Profilen.

# P5 – Stand (2026-11-20)

| Abnahmekriterium P5 | Stand |
| --- | --- |
| Gleiche MCAP-Aufnahme ergibt zweimal dieselbe Task-Folge | erfüllt (`test_mcap_integration.py`: Fahrt im Simulator aufgenommen, auf Rohsensoren gefiltert, zweimal mit SLAM + Burr abgespielt, beide Burr-Läufe identisch, SLAM baut Karte aus der Wiedergabe) |
| Entscheidungs-Replay meldet Abweichungen als Testfehler | erfüllt (`tests/decision_replay/`, 4 Tests; veränderte Entscheidung und veränderte Mission werden gemeldet; echter ROS-Lauf ohne Abweichung nachgespielt) |

Weiter umgesetzt: Dienst `recorder` (Daueraufnahme `/georg/task_manager/*` und `task/current_task` als MCAP, alle Profile, getestet mit denselben Argumenten), Dienst `player` im Profil `mcap` (filtert automatisch auf Rohsensoren), `slam_mcap.launch.py` mit `use_sim_time`, Mock-Szenario `mcap` ohne Odometrie (setzt `projectctl.bash` in `mcap` automatisch).

**Hinweis:** Mit festen Missionen und Mocks hängt die Task-Folge nicht von den Sensordaten ab; „zweimal dieselbe Folge“ ist hier vor allem ein Test der Kette Aufnahme → Filter → Wiedergabe → SLAM → Burr. Aussagekräftig für Entscheidungen wird es mit dem LLM (P6), das auf Ereignisse reagiert.

# P6 – Stand (2026-11-20)

| Abnahmekriterium P6 | Stand |
| --- | --- |
| Im Profil `mock` plant das LLM Missionen, Burr führt sie ohne Eingriff aus | erfüllt, mit echtem lokalem LLM (Qwen2.5-1.5B-Instruct Q4, llama.cpp auf dem Mac): Ziel „Gast klingelt, begrüßen, zum Sitzplatz bringen“ → 4 Entscheidungen, Tasks laufen über die Mock-Pakete, Ende „done“ (`test_llm_real.py`, zweimal identisch) |
| Ungültige Pläne gehen mit Fehlertext zurück, nach der Versuchsgrenze Idle | erfüllt (Test-LLM: 3 ungültige Antworten → FAILED, Fehlertext in der 2. Anfrage) |
| Schlägt ein Task fehl, plant das LLM um oder bricht sauber ab | erfüllt (beide Fälle über ROS mit Test-LLM) |
| Entscheidungs-Replay mit festem Prompt ist stabil | erfüllt, mit dem echten LLM (Temperatur 0, Seed 42): jede Entscheidung zweimal nachgespielt, identisch |
| Betriebsart LLM auf `real` erst nach bestandenen Replay- und Sim-Tests | umgesetzt als Sperre: `set_mode` lehnt LLM-Modi in `real` ab, solange `GEORG_LLM_REAL_APPROVED=1` nicht gesetzt ist. Nicht live getestet (Regel 6: kein Profil `real`). |

Weiter umgesetzt: Missionsblöcke im Katalog (`greet_guest`, `wait_for_guest`), Betriebsarten mission / llm / llm_approval, Services `set_mode`, `instruct`, `approve_plan`, Topic `task_manager/plan`, Panel mit Modus, Anweisung, Freigabe und Planansicht, Entscheidungsprotokoll, Replay von LLM-Entscheidungen, Dienst `llm` (pkg_llm, nur mit `GEORG_WITH_LLM=1`).

**Durch das echte LLM gefundene und behobene Fehler:**
- JSON kennt keinen Unterschied zwischen 60 und 60.0; die ROS-Nachricht `Listen` brach mit einer C-Assertion ab. Zahlen werden jetzt beim Erzeugen der Tasks in float umgewandelt.
- Ohne Schema verwechselte das kleine Modell Tasks und Blöcke; jetzt eingeschränktes Decodieren mit Schema aus dem Katalog.
- Es erfand Orte und antwortete „continue“ ohne Plan; beides wird jetzt abgewiesen.
- Es erkannte das Ende nicht; Kontextfeld `plan_finished` und Prompt `planner-v3`.

**Offen:**
- **Q27 – Modell auf dem Jetson Thor.** Das 1,5B-Modell plant gültig, aber inhaltlich schwach (z. B. „schau zur Tür“ → „auf Klingel hören“). Auf dem Jetson ein größeres Modell wählen und das Image von `pkg_llm` festlegen (für die neuesten llama.cpp-Builds gab es keine nummerierten Image-Tags).
- **Q28 – Ereignisse als Auslöser.** Heute startet nur eine Anweisung der Bedienperson einen LLM-Lauf. Ereignisse (Klingel, Sprache) könnten Läufe direkt auslösen; das ist noch nicht gebaut.

# P7 – Stand (2026-11-21)

Bericht: `docs/hardware_access_report.md`, erzeugt von `tools/hardware_scan.py` (jede getrackte Datei in `packages/` und `system-files/` einzeln, 3218 Dateien, alle im Bericht gelistet).

| Abnahmekriterium P7 | Stand |
| --- | --- |
| Jede Datei in jedem Paket geprüft und im Report gelistet | erfüllt |
| Hardware-Zugriff nur noch in Treiber-Paketen hinter dem `command_gate` | **nicht erfüllt**: 13 Probleme in fremden Paketen (gemeldet, nicht umgebaut, Plan P7 Schritt 4) |
| Offene Funde gemeldet und behoben | gemeldet im Bericht; behoben nur in eigenen Paketen (Task Manager, Navigation) |
| Profil `real` erst danach freigegeben | **gesperrt**: `projectctl.bash up real` verweigert, solange `hardware_scan.py --check` Probleme findet |

Behoben (eigene Pakete): Task Manager ohne `privileged`, nur `/dev/snd` für die Spracherkennung; Navigation leitet in `real` über `cmd_vel/nav` → `twist_mux` → `twist_limiter` → `command_gate` (Q13 erledigt).

Gemeldet an die Paket-Verantwortlichen:
- **pkg_gestures:** `pib-sdk` steuert die Servos des pib per rosbridge am Gate vorbei (heute auskommentiert, Abhängigkeit aber installiert). Servobefehle müssen über ROS-Topics hinter einem Gate laufen.
- **pkg_slam, pkg_viz, pkg_urdf, pkg_examples:** `privileged` bzw. `/dev`-Mounts ohne Bedarf.
- **Offen (nicht prüfbar):** beim Bauen geklonter Code (edu_robot-Treiber, Lidar-Treiber, georg_interfaces, georg_description, RViz-Plugins). Der Treiber `edu_robot` muss `cmd_vel` abonnieren, damit der Remap auf `cmd_vel/gated` greift.

# P8 – Stand (2026-11-21)

Anleitung: `docs/P8_ANLEITUNG.md`.

| Abnahmekriterium P8 | Stand |
| --- | --- |
| Nach dem Einschalten steht Georg in Idle | umgesetzt: `georg.service` startet `projectctl.bash up real`; der Task Manager startet nichts, Betriebsart `mission` (P2/P6 getestet). Auf dem Jetson noch nicht ausprobiert. |
| Ein abgestürzter Container kommt allein wieder hoch | umgesetzt: alle Dauerdienste `restart: unless-stopped` (bzw. `always` beim Treiber), Healthchecks für Task Manager, Gate, Navigation, Gesten, Simulator, Brücke, Burr-UI (`tests/system`). Live-Test mit Docker steht aus. |
| `up real` wird auf dem PC verweigert | erfüllt und getestet (Modusdatei; zusätzlich Sperre durch den Hardware-Scan) |

Umgesetzt: `system-files/etc/systemd/system/georg.service` (Vorlage), `setup-robot.sh` (Modusdatei `real`, Dienst aktivieren), `setup-PC.sh` (Modusdatei `sim`, Lichtblick 1.30.0, Burr-UI als `georg-burr-ui`), `projectctl.bash status`, `GEORG_MODE_FILE` für Tests, `tests/system/test_operation.py` (8 Tests).

**Hinweise:**
- Healthchecks zeigen den Zustand an. Einen laufenden, aber „unhealthy“ Container startet Docker nicht von selbst neu; nur beendete Container werden neu gestartet.
- Der Docker-Installationsteil in `setup-robot.sh` ist für Debian; auf dem Jetson ist Docker meist schon da.
- **Instabiler Test:** `pixi run test_sim_mj` (P3 mit MuJoCo) schlug im Gesamtlauf am 2026-11-21 einmal fehl; vier weitere Läufe direkt danach waren grün. Die Logs zeigen keinen Fehler im Ablauf; welcher der fünf Tests betroffen war, ist nicht mehr feststellbar. Vermutlich ein Zeitproblem unter Last.

# Gesamtstand (2026-11-21)

P0 bis P8 sind umgesetzt. Geprüft auf dem Mac mit ROS 2 Jazzy (RoboStack), nicht im Container und nicht auf dem Roboter. Offen bleiben vor allem:
1. Docker-Build und `up mock`/`up sim` auf einem Rechner mit Docker (P0/P3-Kriterium im Container).
2. Die 13 Probleme aus dem Hardware-Scan in fremden Paketen (P7) – bis dahin bleibt `real` gesperrt.
3. Paket-Vertrag (Ergebnis/Feedback) in den echten Paketen (Q14/Q24), Robotermodell in MuJoCo (Q26), LLM-Modell und Image auf dem Jetson (Q27).

**Q29 – Einheitliche Ordnerstruktur (2026-11-21).** Regeln in der Haupt-README („Aufbau eines Subsystems“): Paketordner = Paketname + `_pkg` (wie `pkg_navigation`), Paketebene bleibt auch bei einem Paket, Paketnamen ohne `georg_` außer bei Nachrichten. Umgesetzt: Ordner `pkg_task_manager/task_manager_pkg/task_manager/`, `georg_task_manager` → `task_manager` (Paket, Python-Modul, Burr-Projekt; alte Burr-Läufe bleiben unter dem alten Projektnamen sichtbar). `pkg_navigation` hält die Regel schon ein und bleibt unverändert. Docker-Build nicht geprüft (kein Docker auf dem Mac).

# Merge von main und Namespace (2026-11-21, Jetson)

`origin/main` (Sams `sim_mode`, Namespace abgeschaltet) in `pkg_task_manager_burr` gemergt; `main` selbst unverändert.

**Entschieden:** Kein Robot-Namespace, wie auf `main` (passt zu pib-backend und Cerebra, die auch ohne arbeiten). Alle eigenen Pakete, Healthchecks, Mocks, Recorder, MCAP-Filter, Lichtblick-Panel/-Layout und Tests folgen jetzt `EDU_ROBOT_NAMESPACE` (Default leer). Zurück auf `georg` geht mit `EDU_ROBOT_NAMESPACE=georg`; dann muss das Panel in Lichtblick auf `/georg` gestellt werden. Services heißen jetzt `/task_manager/start` usw.

**Q30 – `sim_mode` und unser Simulator senden beide Odometrie.** Sams `sim_mode` schaltet nur die Lidar-Treiber ab; `rf2o` läuft weiter und sendet die tf `odom → base_footprint`. Unser Simulator sendet dieselbe tf selbst. Außerdem setzt `sim_mode` `use_sim_time=true`, unser Simulator sendet aber noch kein `/clock`. Deshalb nutzt `pkg_slam` vorerst: `real` → `pkg_slam.launch.py sim_mode:=$GEORG_SIM_MODE` (aus main), `sim`/`mcap` → weiter `slam_sim`/`slam_mcap`. `projectctl.bash` setzt `GEORG_SIM_MODE` noch nicht. Umstellung in Phase 4: Simulator sendet `/clock` und Rad-Odometrie (`odom/wheel`) statt der odom-tf, dann `GEORG_SIM_MODE=true` im Profil `sim` und `drive` startet in `sim` ohne `edu_robot`.

**Q31 – Navigation liest `odom`, auf dem Roboter sendet das niemand (bestehender Fehler, nicht geändert).** `drive_route_action_server.py` abonniert `ODOM_TOPIC = "odom"`. Auf dem Roboter senden `rf2o` `odom/lidar` und der Treiber `odom/wheel`; `odom` senden nur unser Simulator und die Mocks. Vermutlich wartet der Fahrserver in `real` auf Odometrie, die nie kommt. Welche Quelle soll die Navigation nutzen (`odom/lidar`, `odom/wheel` oder fusioniert)? Meldung an die Navigation.

**Fremde Dateien mit `/georg/...` (nicht geändert, an die Verantwortlichen):** `pkg_slam/georg_slam.rviz`, `pkg_viz/config/georg.rviz`, `pkg_viz/georg_slam.rviz` (Topics `/georg/merged_scan`, `/georg/lidar*/scan`, `/georg/odometry`), `pkg_slam/README.md` (Diagramm), `pkg_drive/config/twist_limiter.yaml` (Kommentar). Nach dem Namespace-Wechsel auf `main` zeigen die RViz-Konfigurationen ins Leere.

**Q32 – `command_gate` entfernt, `ROS_DOMAIN_ID` pro Profil (Entscheidung 2026-11-21).** Das Gate prüfte nur Modusdatei und Profil, beides steht beim Start fest und ist schon abgesichert: `drive` startet nur in `real`, Sams `sim_mode` startet in der Sim keinen Treiber, `projectctl.bash up real` verlangt Modusdatei `real` und sauberen Hardware-Scan. In `real` war das Gate immer offen und hätte Befehle einer zweiten Sim im selben Netz durchgelassen. Diese Lücke schließt jetzt `ROS_DOMAIN_ID`: `real` = 0 (wie pib-backend und Cerebra), alle anderen Profile `GEORG_SIM_DOMAIN_ID` (Default 30), Mac-pixi ebenfalls 30. Jeder ROS-Dienst bekommt `ROS_DOMAIN_ID` aus dem Compose. Treiber hört wieder direkt auf `cmd_vel` (wie auf `main`); Q7 ist damit erledigt. Anhalten zur Laufzeit: `twist_mux`-Locks (`vel_locks/pause_navigation`), Vorschlag: Task Manager setzt den Lock bei „Abort“. Hinweis: `docker exec` in einen Sim-Container erbt Domain 30; ein Terminal auf dem Host ohne `ROS_DOMAIN_ID=30` sieht die Sim nicht.

**Q33 – Nach Abbruch in einer Engstelle kommt Georg nicht mehr weg (Navigation, nicht geändert).** Stack-Test auf dem Jetson (Profil `sim`): Abbruch von `sim_door` mitten in der 0,55-m-Lücke zwischen `Wall2` und `Wall3` (Q25). Georg steht danach bei (4,26, −0,72) in einer Zelle, die durch den Sicherheitsabstand (0,25 m) als belegt gilt; `navigate_action_server` meldet „Start position … is in an occupied/out-of-bounds cell“ und lehnt **jedes** weitere Ziel ab. Vorher schickte `drive_route_action_server` 13 s lang denselben Befehl (`vx=-0.18 vy=0.36`), ohne dass Georg vorankam (an der Wand im Simulator) – keine Erkennung „steckt fest“. Vorschläge an die Navigation: Start in einer Sicherheitszelle erlauben (zur nächsten freien Zelle planen), Steckenbleiben erkennen und abbrechen, Engstellen in der Karte prüfen. Wegen Q21 meldet die Mission dabei trotzdem `succeeded`.

**Q34 – Gesten bewegen nichts (Gesten-Paket, nicht geändert).** Im Stack (Profil `sim`) nimmt der echte `pib_gestures_server` `look_at` an und meldet `success: 0`, `message: executed successfully`, sendet aber keinen Gelenkbefehl: In `pib_control.py` ist `pib = Write()` (pib-sdk) auskommentiert, `move_joints()` nutzt `pib` trotzdem. Vorschlag an das Gesten-Team: Gelenkbefehle über den pib-backend-Service `/apply_joint_trajectory` (`datatypes/srv/ApplyJointTrajectory`, Motornamen, rad) schicken. Dann bewegt sich pib in der Sim über `fake_pib_motors` (pkg_pib_model) und auf dem Roboter über pib-backend – ohne pib-sdk, im ROS-Stack, und sichtbar in Lichtblick und Cerebra. `success` ist `int8` statt `bool` (Q14), `0` bedeutet hier offenbar Erfolg.

**Q35 – `map → odom` doppelt in `pkg_slam/config/slam.launch.py` (SLAM, nicht geändert).** Der Launch startet einen `static_transform_publisher` `map → odom` (Identität) **und** `slam_toolbox`, das `map → odom` selbst sendet (`transform_publish_period: 0.02`). Zwei Quellen für dieselbe Transformation: Die SLAM-Korrektur wird überschrieben bzw. die Pose springt. Betrifft `real`. Vorschlag: den statischen Publisher entfernen oder nur ohne `slam_toolbox` starten.

**Q36 – Lokalisierung in der Karte fehlt (Navigation).** `drive_route_action_server` rechnet `Karte = odom + fester Versatz aus der Karten-YAML` (`_load_map_start`). Das stimmt nur, wenn Georg genau am Startpunkt der Karte losfährt und `odom` dort bei 0 beginnt; jede Drift bleibt unkorrigiert, die SLAM-Pose (`map → base_footprint`) wird nicht genutzt. Deshalb nutzt die Sim weiter ihre ideale Odometrie (`odom` = Kartenkoordinaten) und `slam_sim.launch.py`; Sams `sim_mode` gilt in der Sim nur für den Fahrpfad (Q30). Zusammen mit Q31 (`odom` sendet am Roboter niemand) ist das die wichtigste offene Frage vor `real`.
