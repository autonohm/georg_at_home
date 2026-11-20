# pkg_task_manager

> **Layout since P0 (2026-11-20)** – see `docs/task_manager_plan.md`
>
> - This package now contains only the task manager (`georg_task_manager`) and, for the time being, `pib-audio`.
> - Navigation: `packages/pkg_navigation`. Gestures: `packages/pkg_gestures`. Maps: `packages/pkg_slam/maps`.
> - Interfaces (`georg_nav_msgs`, `georg_gesture_msgs`, `georg_task_manager_msgs`): `packages/pkg_interfaces`, built into the base image.
> - The launch file starts only `task_manager`, which runs missions with Burr (P1). The py_trees variant (`task_manager_bt`, `render_mission_bt`) was removed.
> - Start everything with `./projectctl.bash up mock|sim|real|mcap` from the repo root.
>
> The terminal instructions below still work, but each package now runs in its own container.

## Burr engine (since P1)

Missions are executed by an [Apache Burr](https://burr.apache.org/) state machine
(`georg_task_manager/burr_app/`). Tasks and missions are written exactly as before;
only the engine that runs them changed. The priority rules below are unchanged.

The Burr graph is built from the mission at every start: one node per mission step,
named after the task and its most telling argument (`name_arg` in `catalog.yaml`).
A number is only added when the same step occurs twice. The Digital Festival mission
reads as a straight line:

```
start_mission -> listen_doorbell -> gesture_look_at -> gesture_point_to -> listen_speech
              -> gesture_look_at_2 -> gesture_greet_person -> return_to_idle -> finish -> idle
```

Only arrows the priority rules can produce are drawn: a loop on a HIGH/CRITICAL step (retry),
a step back for MID (retry after the next task), and an arrow to `finish` (abort, CRITICAL
failure, done). Each step shows its task, arguments (`args`), result (`last_result`) and where
it goes next (`decision`). A retry shows up as the same node twice in a row.

### Add a new task

1. Write the class in `georg_task_manager/tasks/`, derived from `BaseTask`, with
   `async def run(self, robot, state) -> bool` (see `Gesture.py`).
2. Add one entry to `georg_task_manager/catalog.yaml`: `class` (`module:Class`),
   `action`, `type`, `args_schema` (the constructor arguments), `timeout_s`, `modes`.
   **Tasks that are not in the catalog are rejected at mission start.** The catalog name plus
   the `name_arg` argument become the node name in the Burr graph (e.g. `gesture_look_at`),
   no Burr code needed.
3. Run the tests (see below). `test_validator.py` checks that every catalog class can be imported.

### Add a new mission

1. Copy `georg_task_manager/missions/DigitalFestival.py`; `get_mission()` returns the list of tasks.
2. Add it to `georg_task_manager/mission_selector.py`.
3. Start it: `MISSION_ID=<number>` in `docker-compose.yaml`, or pick it from the menu.

### Burr UI

Every mission run gets its own `burr_app_id` and shows up with all steps and states in the
Burr UI: <http://localhost:7241> (service `burr_ui`, started with every profile).
Project `georg_task_manager`, partition key = mission id.
Tracking is switched off with `GEORG_BURR_TRACKING=0`.

### Tests without ROS

```bash
cd georg_task_manager
pip install "apache-burr[tracking]==0.43.0" pyyaml pytest
python -m pytest test/test_burr_app.py test/test_validator.py
```

ROS message modules are replaced by stand-ins in `test/conftest.py` if they are not installed.
`test_burr_app.py` also compares the Burr engine with the previous loop (`task_manager.py`)
on random scenarios: same task order, same outcome.

This is the Task Manager for the Pib Robot "Georg". It allows the creation of different
tasks, which can be fullfilled in costumized, modular missions by the usage of actions. 
Each task will be fulfilled in sequence and a priority can be assigned.


The priority determines, how the discard of the task is handled by the task manager:

### LOW: 
The task will be discarded after the initial try.

### MID: 
The task will be retried after after a specified amount of time. Another failure will discard the task.

### HIGH: 
The Task will be retried three more times (can be adjusted to the own desire). If the retries are used up, the task will be discarded.
      
### Critical: 
Works the same as the HIGH priority, but instead of just discarding the task, the mission will be stopped after the retries are used up.

# 


# Setup for currently implemented tasks/modules:


## Terminal 1 (for Navigation):

source install/setup.bash

ros2 run navigate_server navigate_action_server --node-name nav_server --action-name nav/navigate

## Terminal 2 (for Drive Tasks):  
source install/setup.bash

ros2 run drive_route_server drive_route_action_server

## Terminal 3 (for Gesture): 
source install/setup.bash

ros2 run pib_gestures_action pib_gestures_server.py 

## If no executable is found:

Execute these terminal commands:
###

cd ~/Task_Manager_Pib/src/pib_gestures_action/modules

chmod +x pib_gestures_client.py

chmod +x pib_gestures_server.py

####

cd ~/Task_Manager_Pib/src/pib_gestures_action/modules/pib_gestures/src/pib_gestures

chmod +x greet_person.py

chmod +x look_at.py

chmod +x point_to.py





## Terminal 4 (for Listen: 
source install/setup.bash

ros2 run voice_assistant listen_action_server

## Terminal 5 (for Task Manager Node):  
source install/setup.bash

ros2 run georg_task_manager task_manager



