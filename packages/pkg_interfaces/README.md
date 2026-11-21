# pkg_interfaces

All ROS interfaces that cross a container boundary. They are built into the base image (`packages/docker_base_image`), so every container has them. This folder has no container of its own (`PKG_IGNORE`).

| ROS package | Content | Used by |
| --- | --- | --- |
| `georg_nav_msgs` | `Navigate.action`, `DriveRoute.action` | pkg_navigation, pkg_task_manager |
| `georg_gesture_msgs` | `PibGesturesInterface.action` | pkg_gestures, pkg_task_manager |
| `georg_speech_msgs` | `Listen.action`, `Say.action`, voice messages | pkg_task_manager, pkg_pib_bridge |
| `georg_task_manager_msgs` | `MissionStatus.msg`, `StartMission.srv`, `CancelMission.srv`, `ListMissions.srv` | pkg_task_manager, Lichtblick (from P2) |

`georg_speech_msgs` was called `datatypes` (from `pib-audio`). Renamed on 2026-11-21: pib-backend has its own, different package `datatypes` (e.g. `PlayAudioFromSpeech`, `ApplyJointTrajectory`), which the base image now builds from the pib-backend repo. Two packages with the same name cannot exist in one workspace.

After changing an interface, rebuild the base image (`./projectctl.bash build_base_image`) and then the containers that use it.
