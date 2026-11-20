# Walkthrough: Create a New Task

This page walks you through adding a new **task** to the Georg task manager, step by step, with a complete example. You do not need prior knowledge of pib or the task manager, but you should be comfortable with Python and `async`/`await`.

> This page is written for a developer who is new to pib and to the task manager. Each section explains the concept first, then shows the code.

---

## Contents

1. [The big picture](#1-the-big-picture)
2. [Glossary](#2-glossary)
3. [Prerequisites](#3-prerequisites)
4. [Step 1: Find an action your task can use](#4-step-1-find-an-action-your-task-can-use)
5. [Step 2: Create the task file](#5-step-2-create-the-task-file)
6. [Step 3: Put the task into a mission](#6-step-3-put-the-task-into-a-mission)
7. [Step 4: Add the mission to the selector](#7-step-4-add-the-mission-to-the-selector)
8. [Step 5: Build and test](#8-step-5-build-and-test)
9. [Choosing a priority](#9-choosing-a-priority)
10. [Pitfalls](#10-pitfalls)
11. [Checklist](#11-checklist)

---

## 1. The big picture

pib is a humanoid robot. **Georg** is the name of this robot's software setup: a set of ROS 2 nodes that each do one job (navigation, gestures, listening, ...).

The **task manager** is the node that decides *what the robot does, in which order*. It does not move the robot itself. Instead:

```
Mission  (an ordered list of tasks)
  └── Task 1  ──► sends an action goal ──► Action server (e.g. gestures) ──► robot moves
  └── Task 2  ──► sends an action goal ──► Action server (e.g. navigation)
  └── ...
```

- A **mission** is a list of tasks that runs top to bottom, for example for an event.
- A **task** is one step in the mission, for example "point at the seat" or "listen for the doorbell".
- An **action** is a ROS 2 request/response with feedback. A task sends an action goal and waits for the result. The action server does the real work.

Your job when writing a task is almost always: **send the right goal to an existing action server, wait for the result, and report success or failure.**

---

## 2. Glossary

| Term | Meaning |
|---|---|
| **ROS 2** | The robot middleware. Nodes talk through topics, services, and actions. |
| **Node** | A running program in ROS 2, e.g. the task manager or the gesture server. |
| **Action** | A long-running request with goal, feedback, and result. Defined in an `.action` file. |
| **Action server** | The node that accepts goals and does the work (e.g. `pib_gestures_server`). |
| **Action client** | The side that sends goals. In this project, the task manager holds the clients. |
| **Task** | A Python class, a subclass of `BaseTask`, with an `async def run(robot, state)` method. |
| **Mission** | A Python function `get_mission()` that returns a list of task objects. |
| **Priority** | How the task manager handles a failed task: `LOW`, `MID`, `HIGH`, `CRITICAL`. |
| **`robot`** | The `Georg` object. Holds all action clients (e.g. `robot.greet_action_client`). |
| **`state`** | The `RobotState` object. Shared flags (e.g. `is_presenting_seat_arm`) that show what is happening. |
| **Camera vector** | A 3D position `(x, y, z)` of the target in mm, in the global coordinate system. |

### Coordinate system

- **x** points away from pib's front (against pib)
- **y** points to pib's right side
- **z** points up

---

## 3. Prerequisites

- The repository cloned: `georg_at_home`
- Access to the robot or the ROS 2 Docker image (see `software/pkg_task_manager/Dockerfile`)
- Python 3, and a ROS 2 environment if you want to run the full system
- Read these files once, they are the reference for everything below:

| File | What to look at |
|---|---|
| `georg_task_manager/georg_task_manager/tasks/base.py` | `BaseTask`, the parent class of every task |
| `georg_task_manager/georg_task_manager/tasks/priority.py` | Priorities and retry counts |
| `georg_task_manager/georg_task_manager/tasks/timeout_watcher.py` | `wait_for_action_result`, which sends a goal and waits |
| `georg_task_manager/georg_task_manager/tasks/Gesture.py` | A complete, simple example task |
| `georg_task_manager/georg_task_manager/Georg.py` | All action clients the robot has |
| `georg_task_manager/georg_task_manager/interface.py` | `RobotState`, all shared state flags |
| `georg_task_manager/georg_task_manager/task_manager.py` | How tasks run and fail |
| `georg_task_manager/georg_task_manager/missions/` | Existing missions |
| `georg_task_manager/georg_task_manager/mission_selector.py` | The mission menu |

---

## 4. Step 1: Find an action your task can use

Ask yourself: *what should the robot do?* Then find the action server that does it.

| Robot ability | Action | Client in `Georg.py` | Package |
|---|---|---|---|
| Gestures (look, point, greet) | `pib_gestures_interface` | `greet_action_client` | `pib_gestures_action` |
| Listen for doorbell or speech | `audio/listen` | `listen_action_client` | `pib-audio` |
| Plan a route to a named place | `nav/navigate_object_x`, `nav/navigate_room_x` | `navigate_object_action_client`, `navigate_room_action_client` | `pkg_navigation` |
| Drive along waypoints | `nav/drive_route` | `drive_route_action_client` | `pkg_navigation` |

For the rest of this walkthrough we use **gestures**, which are easy to see on the robot.

> **Note:** The gesture client in `Georg.py` is named `greet_action_client`, but it sends every gesture (`look_at`, `point_to`, `greet_person`). Use it for gestures and do not be confused by the name.

If the action you need does not exist yet, see the README of the package that owns the action (e.g. `pib_gestures_action/README.md`).

---

## 5. Step 2: Create the task file

### 5.1 Create the file

Create a new file in the tasks folder:

```
software/pkg_task_manager/georg_task_manager/georg_task_manager/tasks/PointToSeat.py
```

Naming convention: one class per file, named the same as the file, in CamelCase.

### 5.2 Write the task

Our example task `PointToSeat` makes pib point its right arm at a target position. Copy this file in full:

```python
# PointToSeat.py
from .base import BaseTask
from .timeout_watcher import wait_for_action_result
from .priority import TaskPriority
from geometry_msgs.msg import Vector3
from pib_gestures_action.action import PibGesturesInterface


class PointToSeat(BaseTask):

    def __init__(self, vx: float, vy: float, vz: float, priority: TaskPriority = TaskPriority.LOW):
        # "PointToSeat" is the name shown in the logs
        super().__init__("PointToSeat", priority)
        self.vx = vx
        self.vy = vy
        self.vz = vz

    async def run(self, robot, state):

        print("[TASK] PointToSeat started")

        # 1. Build the goal, the message that is sent to the gesture server
        goal_msg = PibGesturesInterface.Goal()
        goal_msg.gesture = "point_to"
        goal_msg.camera_vector = Vector3(x=self.vx, y=self.vy, z=self.vz)
        goal_msg.pib_side = "right"
        goal_msg.pib_gesture = "bent_arm"
        goal_msg.pib_hand = "index_finger"

        # 2. Tell the rest of the system what is happening
        state.is_presenting_seat_arm = True

        # 3. Send the goal and wait for the result (max 15 s)
        result = await wait_for_action_result(
            robot.greet_action_client,
            goal_msg,
            timeout=15.0,
            abort_check=lambda: getattr(state, "abort_requested", False),
        )

        state.is_presenting_seat_arm = False

        # 4. Decide: success or failure
        if result is None or result.success != 0:
            print("[TASK] PointToSeat FAILED")
            return False

        state.presented_seat_arm = True
        print("[TASK] PointToSeat finished")
        return True
```

### 5.3 What each part does

| Part | Explanation |
|---|---|
| `class PointToSeat(BaseTask)` | Every task inherits from `BaseTask`. This gives it `name`, `priority`, and `attempts`. |
| `__init__` | Stores the parameters the mission gives you (the target position and the priority). Always call `super().__init__(name, priority)`. |
| `async def run(self, robot, state)` | The only method the task manager calls. It **must** return `True` (success) or `False` (failure). |
| `goal_msg` | The message type comes from the `.action` file. Fill in every field the server uses. |
| `state` flags | Set `..._arm = True` before a movement and back to `False` after it. The flags show what is happening. The `presented_seat_arm = True` flag is set only after success. |
| `wait_for_action_result(...)` | Sends the goal, waits for the result, and cancels the goal on timeout or abort. It returns `None` if the goal was rejected, timed out, or aborted. |
| `abort_check` | Lets the operator stop the mission. If `state.abort_requested` becomes `True`, the goal is cancelled. |
| `result.success != 0` | The gesture server returns `0` for success, `-1` for an error, and `1` for a cancel. |

### 5.4 Keep the structure

Every task in this project follows the same five steps:

1. Build the goal
2. Set state flags (before)
3. Send and wait
4. Clear state flags (after)
5. Return `True` or `False`

Tasks that do not call an action, like `ReturnToIdle`, skip steps 1 and 3 and just set state.

---

## 6. Step 3: Put the task into a mission

A **mission** is a Python file in `georg_task_manager/georg_task_manager/missions/` with a `get_mission()` function that returns a list of tasks.

### 6.1 Create the mission file

Create `missions/PointDemo.py`:

```python
# PointDemo.py
from georg_task_manager.tasks.PointToSeat import PointToSeat
from georg_task_manager.tasks.Gesture import Gesture
from georg_task_manager.tasks.ReturnToIdle import ReturnToIdle
from georg_task_manager.tasks.priority import LOW, MID, HIGH, CRITICAL


# Parameters:
# PointToSeat: (vx, vy, vz, priority)   target position in mm

def get_mission():

    print("[MISSION] Point demo started")

    return [
        Gesture("look_at", -1000.0, 0.0, 100.0),           # look at the guest
        PointToSeat(-2000.0, 0.0, 100.0, priority=MID),    # point at the seat
        ReturnToIdle(),                                    # always end with this
    ]
```

### 6.2 Rules for a mission

- Return a **list**, in the order the tasks should run.
- End with `ReturnToIdle()`. It resets the state flags, so a failed mission does not leave flags set for the next one.
- Pass the priority with a keyword argument (`priority=MID`) so it is clear what the argument is. See [Pitfalls](#10-pitfalls).

---

## 7. Step 4: Add the mission to the selector

The task manager shows a menu when it starts. Missions are registered in `missions/` and selected in `mission_selector.py`.

Open `georg_task_manager/georg_task_manager/mission_selector.py` and make three changes:

```python
from georg_task_manager.missions.DigitalFestival import get_mission as DigitalFestival
from georg_task_manager.missions.Test_Mapping import get_mission as TestMapping
from georg_task_manager.missions.PointDemo import get_mission as PointDemo   # 1. import
import os


def select_mission():
    mission_id = os.environ.get("MISSION_ID")

    if mission_id is None:
        print("\n==================================")
        print("         TASK MANAGER")
        print("==================================")
        print("1 - Digital Festival")
        print("2 - Mapping Test")
        print("3 - Point Demo")                            # 2. menu entry
        print("0 - Exit")

        mission_id = input("\nSelect Mission: ")

    if mission_id == "1":
        return DigitalFestival()

    elif mission_id == "2":
        return TestMapping()

    elif mission_id == "3":                                # 3. selection
        return PointDemo()

    elif mission_id == "0":
        return None

    else:
        print("\nInvalid selection.\n")
```

The `MISSION_ID` environment variable skips the menu, which is useful for scripts and for the launch file. For example, `MISSION_ID=3` starts the Point Demo.

---

## 8. Step 5: Build and test

Test in the order below. Each step builds on the one before it, so stop and fix at the first failure.

### 8.1 Check the syntax (no robot needed)

```bash
python3 -m py_compile georg_task_manager/georg_task_manager/tasks/PointToSeat.py
python3 -m py_compile georg_task_manager/georg_task_manager/missions/PointDemo.py
```

No output means the syntax is correct.

### 8.2 Build the package (ROS 2 environment)

From the ROS 2 workspace (or inside the Docker container):

```bash
colcon build --packages-select georg_task_manager
source install/setup.bash
```

### 8.3 Start the gesture server

In a separate terminal:

```bash
source install/setup.bash
ros2 run pib_gestures_action pib_gestures_server.py
```

Check that the server is available:

```bash
ros2 action list | grep pib_gestures_interface
```

### 8.4 Start the task manager with your mission

```bash
source install/setup.bash
MISSION_ID=3 ros2 run georg_task_manager task_manager
```

Expected output in the log:

```
=== Mission Started ===
[TASK MANAGER] Running Gesture
[TASK] Gesture look_at: Finished successfully
[TASK MANAGER] Running PointToSeat
[TASK] PointToSeat started
[TASK] PointToSeat finished
[TASK MANAGER] Running ReturnToIdle
=== Mission Complete ===
```

### 8.5 Check the failure path

Give the task a target the robot cannot reach, e.g. a point very close to the robot. Ideally the gesture server returns a non-zero result, so your task prints `FAILED`, and with `MID` priority the task manager retries it once after the next task.

> **Known issue:** At the moment the gesture server reports out-of-range targets as success (`result.success` is overwritten with `0`). In that case your task prints `finished` even though the robot did not move. Check the gesture server log for the out-of-range message. See the Known issues section of `pib_gestures_action/README.md`. Until this is fixed, the failure path cannot be tested this way.

### 8.6 Test the logic without a robot

You can test a task without ROS by replacing the action client with a fake one that returns a result:

```python
import asyncio, types
from georg_task_manager.tasks.PointToSeat import PointToSeat
from georg_task_manager.interface import RobotState

class FakeFuture:
    def __init__(self, value): self.value = value
    def add_done_callback(self, cb): cb(self)
    def result(self): return self.value

class FakeHandle:
    accepted = True
    def get_result_async(self):
        return FakeFuture(types.SimpleNamespace(result=types.SimpleNamespace(success=0)))
    def cancel_goal_async(self): return FakeFuture(None)

class FakeClient:
    def wait_for_server(self, timeout_sec=None): return True
    def send_goal_async(self, goal): return FakeFuture(FakeHandle())

class FakeRobot:
    greet_action_client = FakeClient()

ok = asyncio.run(PointToSeat(-2000.0, 0.0, 100.0).run(FakeRobot(), RobotState()))
print("success:", ok)
```

This needs the ROS message packages (`geometry_msgs`, `pib_gestures_action`) on the Python path. Use the ROS 2 environment or stub them. Note that this checks your logic, not the robot's movement. Always run on the robot before a demo.

---

## 9. Choosing a priority

The priority tells the task manager what to do when your task **fails**. It is set per task.

| Priority | On failure | Retries (`MAX_RETRIES`) | Use for |
|---|---|---|---|
| `LOW` (default) | Discarded, mission continues | 0 | Nice-to-have actions, e.g. a look-around |
| `MID` | Requeued after the next task, mission continues | 1 | Actions that work better a bit later |
| `HIGH` | Retried immediately, up to 3 times, then discarded | 3 | Important actions, e.g. greeting a guest |
| `CRITICAL` | Retried up to 3 times, then the **whole mission stops** | 3 | Actions without which the mission makes no sense |

From `task_manager.py`:

- `LOW`: one attempt, discard on failure.
- `MID`: after a failure, the task is inserted at position 1, so it runs after the next task.
- `HIGH` / `CRITICAL`: the task is put back at the front of the queue and retried right away.
- `CRITICAL`: after the retries are used up, the mission is aborted.

---

## 10. Pitfalls

These are real mistakes found in the existing code. Avoid them in your task.

| Pitfall | What happens | Fix |
|---|---|---|
| **Positional priority argument** | `Listening("DOORBELL", HIGH)` in `DigitalFestival.py` passes `HIGH` as the *timeout*, not as the priority. | Use keywords: `Listening("DOORBELL", priority=HIGH)`. Check the parameter order of the `__init__`. |
| **Forgetting to clear a state flag** | Other tasks see a stale `True`, e.g. "still presenting". | Clear flags in every exit path, also on failure. |
| **Returning `None`** | `run()` must return `True` or `False`. `None` is treated as a failure in the mission flow. | Always end with `return True` or `return False`. |
| **Sending a goal to the wrong client** | The robot does the wrong action or nothing. | Check the client name in `Georg.py` and the action name. |
| **Wrong gesture name** | The server rejects the goal with `faulty gesture selection`. | Use the exact names: `look_at`, `point_to`, `greet_person`. |
| **Wrong pib side, gesture or hand** | The client or the server rejects the value. | Use keys from `pib_gestures/config/gestures.py`. |
| **No timeout** | A stuck action blocks the mission forever. | Always pass `timeout=` to `wait_for_action_result`. |
| **Blocking calls in `run()`** | `time.sleep()` blocks the event loop. | Use `await asyncio.sleep(...)`. |
| **Mission without `ReturnToIdle()`** | The next mission starts with stale flags. | Add `ReturnToIdle()` at the end. |
| **Mission name not in the selector** | The menu does not show it and `MISSION_ID` gives "Invalid selection". | Complete [Step 4](#7-step-4-add-the-mission-to-the-selector). |

---

## 11. Checklist

Before you open a pull request, check each point:

- [ ] Task file in `georg_task_manager/georg_task_manager/tasks/`, named like the class
- [ ] Inherits from `BaseTask`, calls `super().__init__(name, priority)`
- [ ] `run(self, robot, state)` is `async` and returns `True` or `False`
- [ ] Uses an existing action client from `Georg.py`
- [ ] Passes a `timeout=` and an `abort_check`
- [ ] Sets state flags before and clears them after, also on failure
- [ ] Mission file in `missions/` with `get_mission()` returning a list
- [ ] Mission ends with `ReturnToIdle()`
- [ ] Mission added to `mission_selector.py` (import, menu line, `elif`)
- [ ] `py_compile` passes
- [ ] Tested with a fake robot or on the robot
- [ ] Tested the failure path
- [ ] Priority chosen on purpose (see [section 9](#9-choosing-a-priority))

---

## Where to go next

- `pib_gestures_action/README.md`: add a new gesture to the server
- `pkg_navigation/README.md`: navigation and driving actions
- `pib-audio/README.md`: listening actions
- `maps/README.md`: map files and named objects
