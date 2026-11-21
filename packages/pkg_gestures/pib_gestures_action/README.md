# pib_gestures_action

ROS 2 action interface and server/client for the gestures of the pib robot "Georg".
The package exposes one action, `pib_gestures_interface`, that lets the Task Manager (or any other ROS 2 node) trigger a gesture such as looking at, pointing to, or greeting a person. The gesture math lives in the pure-Python package `pib_gestures` (`modules/pib_gestures`), which the action server calls.

## Package layout

```
pib_gestures_action/
├── modules/
│   ├── pib_gestures_server.py        # ROS 2 action server (dispatches gestures)
│   ├── pib_gestures_client.py        # CLI action client for manual tests
│   └── pib_gestures/                 # Pure-Python gesture library (pip package "pib-gestures")
│       ├── src/pib_gestures/
│       │   ├── core/                 # One module per gesture (look_at, point_to, greet_person)
│       │   ├── config/               # gestures.py (mode names), param.py (joint limits, DH params)
│       │   ├── utils/                # transform.py, logic.py, pib_control.py
│       │   └── classes/              # vector and matrix helpers
│       └── tests/
├── CMakeLists.txt                    # Installs server/client scripts
└── package.xml
```

## Action interface

Defined in `packages/pkg_interfaces/georg_gesture_msgs/action/PibGesturesInterface.action` (ROS package `georg_gesture_msgs`):

```
# Goal
string gesture
geometry_msgs/Vector3 camera_vector
string pib_side
string pib_gesture
string pib_hand
---
# Result
int8 success
string message
---
# Feedback
string status
```

| Field | Meaning |
|---|---|
| `gesture` | **Required.** Which core function to run: `look_at`, `point_to`, `greet_person`. Empty goals are rejected. |
| `camera_vector` | Position of the target in the global coordinate system (see below), in mm. |
| `pib_side` | `left`, `right`, or `none` (auto-selected by the logic). Used by `point_to` and `greet_person`. |
| `pib_gesture` | `straight_arm`, `bent_arm`, `wave`, `shake_hands`, `look`, or `none`. Valid names are the keys of `gestures.pib_gesture`. |
| `pib_hand` | `index_finger`, `open_hand`, or `none`. Used by `point_to`. |

**Result codes** (`success`):

| Value | Meaning |
|---|---|
| `0` | Executed successfully |
| `-1` | Exception during execution (see `message`) |
| `1` | Client canceled the request |

**Coordinate system:** x points away from pib's front (against pib), y points to pib's right side, z points up.

Feedback is currently not published by the server.

## Build

From your ROS 2 workspace:

```bash
colcon build --packages-select pib_gestures_action
source install/setup.bash
```

The `.action` file is compiled by `rosidl_generate_interfaces`, so after changing it you must rebuild and re-source before the Python import `from georg_gesture_msgs.action import PibGesturesInterface` picks up the new fields.

## Running the server

```bash
source install/setup.bash
ros2 run pib_gestures_action pib_gestures_server.py
```

The node is named `pib_gestures_server` and serves the action `pib_gestures_interface`. The Task Manager launch file (`pkg_task_manager/config/task_manager.launch.py`) starts it the same way.

## Running the client (manual test)

```bash
source install/setup.bash
ros2 run pib_gestures_action pib_gestures_client.py <gesture> <x> <y> <z> [pib_side] [pib_gesture] [pib_hand]
```

Examples:

```bash
ros2 run pib_gestures_action pib_gestures_client.py look_at -1000 500 -200
ros2 run pib_gestures_action pib_gestures_client.py point_to -1000 0 500 right bent_arm index_finger
ros2 run pib_gestures_action pib_gestures_client.py greet_person -1000 0 0 right wave
```

Omitted optional arguments default to `none`, so the logic chooses the side, gesture, or hand itself.

## Using the action from the Task Manager

The Task Manager creates the client in `georg_task_manager/georg_task_manager/robot.py`:

```python
self.greet_action_client = ActionClient(node, PibGesturesInterface, "pib_gestures_interface")
```

A task is a `BaseTask` subclass in `georg_task_manager/georg_task_manager/tasks/`. `tasks/Gesture.py` shows the pattern:

```python
goal_msg = PibGesturesInterface.Goal()
goal_msg.gesture = self.mode
goal_msg.camera_vector = Vector3(x=self.vx, y=self.vy, z=self.vz)
goal_msg.pib_side = "right"
goal_msg.pib_gesture = "wave"
goal_msg.pib_hand = "open_hand"

result = await wait_for_action_result(robot.greet_action_client, goal_msg, timeout=15.0, abort_check=...)
if result is None or result.success != 0:
    return False
return True
```

## How to add a new gesture (action)

Adding a gesture touches four places. Example: a gesture called `nod`.

### 1. Write the core function

Create `modules/pib_gestures/src/pib_gestures/core/nod.py`. Follow the structure of `look_at.py` and `point_to.py`:

```python
'''
core functionality of nod:
transformation of camera vector into vector from center to object (DH matrices)
calculation of head joint angles
checking joint limits
moving joints for the gesture
'''
from ..utils import transform, pib_control
from ..config import param, gestures

import time


def nod(object_vector_x, object_vector_y, object_vector_z) -> int:
    # 1. camera vector -> vector from robot center to object
    object_vector_center = transform.calculate_object_vector_center(
        object_vector_x, object_vector_y, object_vector_z)

    # 2. joint angles for the head (reuse the look_at helpers)
    object_vector_head = transform.calculate_head_vector(object_vector_center)
    q_head = transform.calculate_joint_angles_for_head_vector(object_vector_head)

    # 3. limit check: return 1 if the target cannot be reached
    if not transform.check_head_joint_limits(q_head, object_vector_head):
        return 1

    # 4. correct rotation directions for this pib unit
    q_head = transform.adjust_joint_rotation_direction(q_head, 'head')

    # 5. move joints (pib_control is currently commented out in the existing gestures)
    # pib_control.move_joints(head, q_head)

    time.sleep(1)
    return 0   # 0 = success, 1 = target out of range
```

Conventions used by all existing core functions:

- Signature starts with the camera vector `x, y, z`, followed by optional gesture parameters with defaults from `gestures`.
- Return `0` on success and `1` if the target is out of range or joint limits are violated.
- Use the helpers in `utils/transform.py` and `utils/logic.py`. Do not hard-code joint directions; use `param.joint_invert`.

### 2. Export the function

Add the import to `modules/pib_gestures/src/pib_gestures/core/__init__.py`:

```python
from .nod import nod
```

### 3. Register the gesture name and parameters (if needed)

- New **modes, sides, or hands** go into `config/gestures.py` (`pib_gesture`, `pib_side`, `pib_hand` dictionaries) together with their angles, e.g. entries in `arm_gesture_joint_angles`.
- New **joint limits or DH parameters** go into `config/param.py`.
- A pure head gesture like `nod` needs no new entries if it only uses `head` joints.

### 4. Wire it into the server

In `modules/pib_gestures_server.py`, import the function and add a branch to `execute_callback`:

```python
from pib_gestures.src.pib_gestures.core import look_at, point_to, greet_person, nod

...
elif self.goal.gesture == "nod":
    result.success = nod(
        self.goal.camera_vector.x,
        self.goal.camera_vector.y,
        self.goal.camera_vector.z,
    )
```

Add the same name to `modules/pib_gestures_client.py` if you want to test it from the CLI, and to `usage_info()` so the help text stays correct.

### 5. Build, test, and call it

```bash
colcon build --packages-select pib_gestures_action
source install/setup.bash
ros2 run pib_gestures_action pib_gestures_server.py      # terminal 1
ros2 run pib_gestures_action pib_gestures_client.py nod -1000 0 0   # terminal 2
```

Then add a task in `georg_task_manager/tasks/` (copy `Gesture.py`, change the name and fields) and use it in a mission.

### Adding a new action *type* (not a new gesture)

If you need a new kind of request, for example a `pib_speed` field or a second result field, you must:

1. Add the field to `pkg_interfaces/georg_gesture_msgs/action/PibGesturesInterface.action`.
2. Rebuild the interface package (`colcon build --packages-select georg_gesture_msgs`) so that server, client, and Task Manager all get the new type.
3. Set and read the field in the server, client, and any task that uses it.

Changing the action definition breaks any node that was built against the old version, so rebuild all dependent packages.

## Known issues

These are visible in the current code. They are listed here so you know what to expect before fixing them.

- **Motion is disabled.** In all core functions, the calls to `pib_control.move_joints(...)` and the `pib_control.set_up_pib()` call are commented out (`###`). The gestures compute joint angles and look/wait, but they do not move the robot yet.
- **Out-of-range targets report success.** `execute_callback` sets `result.success` from the core function (`1` means out of range), but then overwrites it with `0` after `goal_handle.succeed()`. Check the logs rather than the result code until this is fixed.
- **Exception handling assigns an exception object to a string.** `result.message = error_message` in the `except` branch passes an `Exception`, not a `str`. Use `str(error_message)`.
- **Mismatched attribute name in the server.** `execute_callback` sets `self.goal_running`, while `goal_callback` checks `self._goal_running`. The one-goal-at-a-time check therefore never triggers.
- **Client side check uses the wrong variable.** `pib_gestures_client.py` validates `goal_msg.pib_side` (a local, unpopulated object) instead of `self.goal_msg.pib_side`, so invalid side names are not caught.
- **Import path.** The server and client import `pib_gestures.src.pib_gestures.core` and `pib_gestures.config`. This works only when the repository root is on `PYTHONPATH`. Installing `pib-gestures` as a pip package (`modules/pib_gestures/pyproject.toml`) and importing `pib_gestures.core` is the cleaner option.
- **Hard-coded values in the Task Manager.** `tasks/Gesture.py` always sends `pib_side="right"`, `pib_gesture="wave"`, and `pib_hand="open_hand"`, regardless of the gesture requested.

## Troubleshooting

- **`Goal rejected` in the client:** the goal was empty (`gesture` missing) or the server is already running a goal.
- **`pib side is faulty` / `pib gesture is faulty` / `pib hand is faulty`:** the value is not a key of `gestures.pib_side`, `gestures.pib_gesture`, or `gestures.pib_hand`. Run the client without arguments to see the valid names.
- **`ModuleNotFoundError: pib_gestures`:** the Python package is not importable. Install `modules/pib_gestures` with pip, or add the repository root to `PYTHONPATH`.
- **`ModuleNotFoundError: georg_gesture_msgs.action`:** the interface package was not built or sourced. Run `colcon build --packages-select georg_gesture_msgs` and `source install/setup.bash`.
- **Gesture returns `1`:** the target is outside the reachable range or joint limits. Move the target closer or check the coordinate system.

## License

See `LICENSE`.
