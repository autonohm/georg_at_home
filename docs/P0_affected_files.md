# P0 – Betroffene Dateien und Imports (vor dem ersten Verschieben)

Stand: 2026-11-20, Branch `pkg_task_manager_burr`. **Umgesetzt**, außer `pib-audio` (zurückgestellt, siehe OPEN_QUESTIONS Q1). Interfaces liegen in `pkg_interfaces` und werden ins Basis-Image gebaut statt per Build-Kontext in jeden Container.

## 1. Verschiebungen (`git mv`)

| Von | Nach | Getrackte Dateien | ROS-Pakete darin |
| --- | --- | --- | --- |
| `packages/pkg_task_manager/pkg_navigation` | `packages/pkg_navigation` | 42 | `navigate_server`, `drive_route_server` (Duplikat gelöscht) |
| `pkg_navigation/georg_nav_msgs` | `packages/pkg_interfaces/georg_nav_msgs` | – | `georg_nav_msgs` |
| `pib_gestures_action/action/PibGesturesInterface.action` | `packages/pkg_interfaces/georg_gesture_msgs/action/` | 1 | neu: `georg_gesture_msgs` |
| `packages/pkg_task_manager/pib_gestures_action` | `packages/pkg_gestures/pib_gestures_action` | 40 + Gitlink `modules/pib_sdk` | `pib_gestures_action` |
| `packages/pkg_task_manager/pib-audio` | bleibt vorerst (Q1) | 31 | `voice_assistant`, `datatypes` |
| `packages/pkg_task_manager/maps` | `packages/pkg_slam/maps` | 2 | – |

Python-Imports ändern sich durch die Verschiebung **nicht**: ROS-Paketnamen kommen aus `package.xml`, nicht aus dem Pfad.

## 2. Dateien, die angepasst werden (nur Pfade, Dockerfiles, Compose, Launch)

**`pkg_task_manager`**
- `Dockerfile`: `COPY` für `pib_gestures_action`, `pib-audio`, `pkg_navigation`, `maps` entfernen. Audio-/TensorFlow-Pip-Pakete und `portaudio19-dev` wandern ins Speech-Dockerfile.
- `docker-compose.yaml`: Volume `./maps` und `GEORG_MAP_*` entfernen, `profiles` ergänzen, `privileged: true` prüfen (Q6).
- `config/task_manager.launch.py`: Nav-, Drive-, Gesten- und Voice-Node entfernen (gehen in die Paket-Launches). Nur noch **ein** Task-Manager-Node (Q2).
- `georg_task_manager/package.xml`: Abhängigkeiten `georg_msgs`, `georg_nav_action`, `pib-audio` existieren nicht als Pakete (Q5).
- `README.md`, `wiki/Create-a-New-Task.md`: Pfade.

**Neu**
- `packages/pkg_navigation/{Dockerfile,docker-compose.yaml,config/navigation.launch.py}`
- `packages/pkg_gestures/{Dockerfile,docker-compose.yaml,README.md,config/gestures.launch.py}`
- `packages/pkg_speech/{Dockerfile,docker-compose.yaml,config/speech.launch.py}`, `PKG_IGNORE` entfernen (Q1)
- `packages/pkg_interfaces/` (aus `pkg_examples/pib_action_template`: `MissionStatus.msg`, `StartMission.srv`, `CancelMission.srv`, `ListMissions.srv`)
- `packages/pkg_command_gate/` oder Node in `pkg_drive` (Q7)
- `compose.yaml` im Repo-Root mit `include` und Profilen `mock`, `sim`, `real`, `mcap`

**Weitere**
- `projectctl.bash`: `up <modus>`, Prüfung `/etc/georg/mode`, Ablehnung von `real` außerhalb des Roboters.
- `system-files/projectctl-completion.bash`: vier Modi; Pfad `software/pkg_*` → `packages/pkg_*` (heute falsch).
- `packages/pkg_slam/{Dockerfile,docker-compose.yaml}`: Maps einbinden.
- `packages/pkg_navigation` braucht Maps aus `pkg_slam/maps` (Volume `../pkg_slam/maps`).

## 3. Container-übergreifende Abhängigkeiten des Task Managers

Der Task Manager baut heute alle Pakete im selben Workspace. Nach der Trennung braucht sein Container trotzdem:

| Import im Task Manager | Kommt aus | Dateien |
| --- | --- | --- |
| `georg_nav_msgs.action` | `pkg_navigation/georg_nav_msgs` | Georg.py, tasks/Navigate*, tasks_bt/Navigate_BT.py |
| `pib_gestures_action.action` | `pkg_gestures/pib_gestures_action` | Georg.py, tasks/Gesture.py, tasks_bt/Gesture_BT.py |
| `datatypes.action.Listen` | `pkg_speech/pib-audio/src/datatypes` | Georg.py, tasks/Listening.py, tasks_bt/Listening_BT.py |
| `navigate_server.grid_rasterizer` (Python-Code, keine Schnittstelle) | `pkg_navigation/navigate_server_pkg` | tasks/NavigateObject.py, tasks/NavigateRoom.py, tasks_bt/Navigate_BT.py |
| `grasp_planning.action` | nicht im Repo | nur verschachtelte Kopie `georg_task_manager/georg_task_manager/georg_task_manager/tasks/GraspPlanning.py` |

Siehe Q4.
