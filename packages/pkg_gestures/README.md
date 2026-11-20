# pkg_gestures

Gesture subsystem of Georg as its own container. Moved out of `pkg_task_manager` in P0.

| Part | Path |
| --- | --- |
| Action server and client | [pib_gestures_action/](pib_gestures_action/README.md) |
| Action definition | [../pkg_interfaces/georg_gesture_msgs/](../pkg_interfaces/georg_gesture_msgs/action/PibGesturesInterface.action) |
| Launch file | `config/gestures.launch.py` |

Runs in the compose profiles `sim` and `real`. Start it with `./projectctl.bash up sim`.

`pib-sdk` is installed with pip in the `Dockerfile`. It replaces the former git submodule `modules/pib_sdk`, which had no `.gitmodules` entry. All `pib_sdk` imports in the gesture code are commented out at the moment, so gestures do not move motors yet.
