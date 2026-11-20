# pkg_task_manager

> **Layout since P0 (2026-11-20)** – see `docs/task_manager_plan.md`
>
> - This package now contains only the task manager (`georg_task_manager`) and, for the time being, `pib-audio`.
> - Navigation: `packages/pkg_navigation`. Gestures: `packages/pkg_gestures`. Maps: `packages/pkg_slam/maps`.
> - Interfaces (`georg_nav_msgs`, `georg_gesture_msgs`, `georg_task_manager_msgs`): `packages/pkg_interfaces`, built into the base image.
> - The launch file starts only the sequential `task_manager`. `task_manager_bt` (py_trees) is no longer launched and will be replaced by Burr in P1.
> - Start everything with `./projectctl.bash up mock|sim|real|mcap` from the repo root.
>
> The terminal instructions below still work, but each package now runs in its own container.

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

or

source install/setup.bash

ros2 run georg_task_manager task_manager_bt


## Rendering the BT Mission

source install/setup.bash 

ros2 run georg_task_manager render_mission_bt x

Set x to Mission ID
