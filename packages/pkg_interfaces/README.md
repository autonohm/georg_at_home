# pkg_interfaces

All ROS interfaces that cross a container boundary. They are built into the base image (`packages/docker_base_image`), so every container has them. This folder has no container of its own (`PKG_IGNORE`).

| ROS package | Content | Used by |
| --- | --- | --- |
| `georg_nav_msgs` | `Navigate.action`, `DriveRoute.action` | pkg_navigation, pkg_task_manager |
| `georg_gesture_msgs` | `PibGesturesInterface.action` | pkg_gestures, pkg_task_manager |
| `georg_task_manager_msgs` | `MissionStatus.msg`, `StartMission.srv`, `CancelMission.srv`, `ListMissions.srv` | pkg_task_manager, Lichtblick (from P2) |

`datatypes` (`Listen.action`, voice messages) still lives in `pkg_task_manager/pib-audio` until the state of the speech package is clear.

After changing an interface, rebuild the base image (`./projectctl.bash build_base_image`) and then the containers that use it.
