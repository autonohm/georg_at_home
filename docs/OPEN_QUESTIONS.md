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

**Q11 – Bauen.** Nicht verifiziert. Auf dem Mac fehlen colcon und ROS, der Docker-Daemon antwortete nicht, und es sind nur 5,9 GB frei. Allein der Task-Manager-Container zieht TensorFlow und faster-whisper, das reicht nicht. Optionen: Windows-Remote-PC mit Docker Desktop (WSL2), oder Jetson. Auf dem Jetson darf nur bis `build` gegangen werden, `up real` erst nach P7.

## Neu gefunden (bestehende Fehler, nicht behoben)

**Q12 – Action-Namen passen nicht.** Der Launch startet den Navigationsserver unter `/nav/navigate` (absolut). Der Task Manager ruft `nav/navigate_object_x` und `nav/navigate_room_x` im Namespace `georg` auf. Ein Server bedient nur einen Namen. In `pkg_navigation/config/navigation.launch.py` unverändert übernommen und mit TODO markiert. Welche Namen sollen gelten?

**Q13 – Navigation umgeht `twist_limiter`.** `drive_route_server` sendet direkt auf `cmd_vel`, nicht auf `cmd_vel/nav` (Eingang von `twist_mux`). Damit greifen weder `twist_mux` noch `twist_limiter`. Das verstößt gegen die harte Regel „Bewegung nur über Paket-Actions mit eigenen Grenzen“. Das Gate fängt den Weg außerhalb von `real` ab, auf dem Roboter aber nicht. Fix ist eine Zeile in der Navigation, also Logik: freigeben?

**Q14 – Gesten-Result entspricht nicht dem Paket-Vertrag.** `PibGesturesInterface` liefert `int8 success` statt `bool success`, `string error_code`, `string message`. Feedback ist `string status` statt `phase` und `progress`. Unverändert, Anpassung mit dem Gesten-Verantwortlichen.

**Q15 – Kleinkram.** `navigate_server` registriert `fake_odom` aus `odom_sim.py`, die Datei fehlt (gab es nur noch als `.pyc`). `docker_base_image/compose.yaml` taggt `georg-ros:humble`, alles andere nutzt `jazzy`. `projectctl.bash install_completion` zeigte auf `packages/projectctl-completion.bash`, korrigiert auf `system-files/`.
