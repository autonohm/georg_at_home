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

**Q4b – `navigate_server.grid_rasterizer` im Task Manager.** `NavigateObject`/`NavigateRoom` lesen die Karte selbst. Übergangslösung: `navigate_server` wird im Task-Manager-Container mitgebaut (zusätzlicher Build-Kontext). Vorschlag für P1: Task Manager schickt nur den Objektnamen, die Navigation löst ihn auf.

**Q5 – erledigt durch Umbau.** Ungültige Abhängigkeiten `georg_msgs`, `georg_nav_action`, `pib-audio` in `georg_task_manager/package.xml` ersetzt durch `georg_gesture_msgs`, `datatypes`, `georg_nav_msgs`. Bitte kurz bestätigen.

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

**Q23 – `MISSION_ID` entfernt.** Der Node `task_manager` ist jetzt die Brücke und startet nach dem Booten nichts. Die alte Variante mit `MISSION_ID` heißt `task_manager_cli`. Im Compose ist `MISSION_ID` entfernt.

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
