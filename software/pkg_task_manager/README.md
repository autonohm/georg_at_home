# pkg_task_manager

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





## Terminal 4 (for Listen): 
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

# Using a pib-backend service as a task

A service from the pib-backend is called in the Task Manager as a ROS 2 service client. The service server stays in the backend container. In the Task Manager container, only the client is created and the request is sent.

### 1. Check the service interface and reachability

Find out the ROS 2 service type, its name, and the request/response fields. For the Speak service, for example:

```bash
ros2 interface show datatypes/srv/PlayAudioFromSpeech
ros2 service list -t
```

The type must be available in the Task Manager container. The base image already includes the pib_backend `datatypes` package.

The container running the service must be up and in the same network as the Task Manager. This is ensured in `docker-compose.yaml`:

```yaml
networks:
  pib-network:
    external: true
    name: pib-network
```

If it does not work automatically, check:

```bash
docker network ls
docker network inspect pib-network --format '{{range .Containers}}{{.Name}} {{end}}'
```

### 2. Add the service type as a package dependency

The package providing the service type must be listed as a dependency in `georg_task_manager/package.xml`:

```xml
<depend>datatypes</depend>
```

This ensures that the Python import is available in the Task Manager. 

### 3. Register the client in the robot interface

Import the generated service type and create the client once when initializing the robot interface in `georg_task_manager/Georg.py`:

```python
from datatypes.srv import PlayAudioFromSpeech

self.speak_service_client = node.create_client(
    PlayAudioFromSpeech,
    "/play_audio_from_speech",
)
```

Use the name under which the server is actually registered. An absolute name such as `/play_audio_from_speech` makes sense if the server lives outside the robot namespace; relative names are completed with the client's namespace.

### 4. Implement the task as a `BaseTask`

Create a file under `georg_task_manager/tasks/`. The task receives the robot interface and the state in `run`, sets the request fields according to the service interface, and waits for the response using `wait_for_service_result`:

```python
from .base import BaseTask
from .timeout_watcher import wait_for_service_result
from .priority import TaskPriority
from datatypes.srv import PlayAudioFromSpeech


class Speak(BaseTask):
    def __init__(self, text: str, priority=TaskPriority.LOW):
        super().__init__("Speak", priority)
        self.text = text

    async def run(self, robot, state):
        request = PlayAudioFromSpeech.Request()
        request.speech = self.text
        request.gender = "M1"
        request.language = "de"
        request.join = True

        response = await wait_for_service_result(
            robot.speak_service_client,
            request,
            timeout=60.0,
            abort_check=lambda: getattr(state, "abort_requested", False),
        )
        return response is not None
```

Adapt the client attribute, request fields, and timeout to the respective service.

`wait_for_service_result` waits for a limited time for the service to become available and for the result. It returns `None` if the service is missing, on timeout, on abort, or on a service error.

Return `True` on success and `False` on failure, so that the Task Manager can apply the configured task priority and retry logic. If the response contains a success field, evaluate it as well.

### 5. Add the task to a mission

Import the task in a mission and insert it into the task list at the desired position. A mission that only speaks returns a list with exactly one task:

```python
from georg_task_manager.tasks.Speak import Speak


def get_mission():
    return [Speak("Hallo, ich bin Georg.")]
```

Also register the mission in the mission selector and select its ID via `MISSION_ID`. For the existing Speak-only mission, the ID is `3`.

### 6. Test the service and the task separately

First check that the backend container is running and that the service is visible in the ROS network:

```bash
ros2 service list -t | grep play_audio_from_speech
```

Test the service independently of the Task Manager with a direct call:

```bash
ros2 service call /play_audio_from_speech \
  datatypes/srv/PlayAudioFromSpeech \
  "{speech: 'Hallo, ich bin Georg.', gender: 'M1', language: 'de', join: true}"
```

If this call works, start the Task Manager with the appropriate mission ID.

If the service is not visible, check in this order:

1. ROS network (`pib-network`)
2. `ROS_DOMAIN_ID`
3. Service name
4. Availability of the generated service interface in the Task Manager container