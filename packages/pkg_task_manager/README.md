# pkg_task_manager

Runs Georg's missions: a mission is a list of tasks (drive, gesture, pose, speak, listen, …);
the Burr state machine executes them, the catalog defines which tasks exist, an optional LLM
plans them. Overview: [../../README.md](../../README.md), operation: [docs/OPERATIONS.md](../../docs/OPERATIONS.md).

- Services `/task_manager/{start,cancel,list_missions,set_mode,instruct,approve_plan}`, status
  `/task_manager/status`, plan `/task_manager/plan`. The node starts idle; nothing runs at boot.
- Tasks talk to packages by actions only (`nav/...`, `pib_gestures_interface`, `pib/pose`,
  `speech/say`, `audio/listen`, `sim/reset`); interfaces in `packages/pkg_interfaces`.
- Same container image also runs `mock_packages` (fake action servers), `recorder` (MCAP) and
  `burr_ui` (port 7241).

## Layout

```
task_manager_pkg/                ROS package task_manager (package.xml, setup.py, test/)
task_manager_pkg/task_manager/   Python code
  node.py        ROS node: services, status topic, mode switch (entry point task_manager)
  robot.py       action clients to speech, gestures, navigation; odom
  state.py       RobotState (position, current task)
  engine/        Burr: graph builder, actions, LLM actions, TaskManagerService (no ROS)
  catalog/       catalog.yaml (allowed tasks + blocks), loader.py, validator.py
  planner/       LLM planner: client, prompts, JSON schema, decision log
  tasks/         one class per task (Gesture, Listening, NavigateObject, ...)
  missions/      one file per mission; registry MISSIONS in missions/__init__.py
  mocks/         fake action servers + scenarios (entry point mock_packages)
task_manager_pkg/test/  tests (unit without ROS, ROS/sim/MCAP/LLM integration with env flags)
```

## Burr engine (since P1)

Missions are executed by an [Apache Burr](https://burr.apache.org/) state machine
(`task_manager/engine/`). Tasks and missions are written exactly as before;
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

### Start and cancel missions (P2)

The task manager node starts in Idle and never starts a mission by itself.
Missions are started and cancelled via services (namespace `georg` by default):

```bash
ros2 service call /task_manager/list_missions georg_task_manager_msgs/srv/ListMissions "{}"
ros2 service call /task_manager/start georg_task_manager_msgs/srv/StartMission "{mission_id: digital_festival}"
ros2 service call /task_manager/cancel georg_task_manager_msgs/srv/CancelMission "{}"
ros2 topic echo /task_manager/status --qos-durability transient_local
```

`StartMission` is rejected with a reason if a mission is running, the mission is unknown,
a task is not in the catalog or not allowed in the current mode, or **an action server
the mission needs is not reachable** (checked before the start). `CancelMission` cancels
the running action goal and ends the mission as `ABORTED`.

Missions that can be started are listed in `missions/__init__.py` (`MISSIONS`).

### Mock packages (P2)

`ros2 run task_manager mock_packages --scenario <name>` provides fake action servers for
speech, gestures and navigation (same names and types as the real packages) plus `odom`.
Scenarios are in `task_manager/mocks/scenarios/`:

| Scenario | Effect |
| --- | --- |
| `all_ok` | every package succeeds |
| `one_fails` | the gesture package always fails |
| `retry_then_ok` | the gesture fails once, then works |
| `timeout` | the speech package never answers |
| `abort` | driving takes 30 s, time to cancel |
| `unreachable` | no drive server, the start is rejected |

In compose profile `mock` they run as service `mock_packages`
(scenario via `GEORG_MOCK_SCENARIO`). The mission `mock_test` uses every package once.
`test/test_ros_integration.py` runs all mandatory scenarios automatically
(`GEORG_ROS_TESTS=1`, needs ROS; on a Mac `pixi run test_ros`, see `dev/macos/`).

### LLM planner (P6)

After the start the task manager is always in mode `mission`. The operator can switch to
`llm` or `llm_approval` (Lichtblick panel or `task_manager/set_mode`); then an instruction
(`task_manager/instruct`) starts an LLM run:

```
start_llm -> next -> <task or block> -> next -> ... -> finish -> idle      (star graph)
```

- `next` asks the planner (`task_manager/planner/`) after every task: new plan,
  continue, done or abort. The planner talks to a local LLM over HTTP (`GEORG_LLM_URL`,
  OpenAI-compatible, see `packages/pkg_llm`).
- Guard rails: JSON schema from the catalog (constrained decoding), then the validator
  (catalog names, arguments, mode, preconditions, places of the map, max. 8 steps).
  Invalid answers go back to the LLM with the error text; after 3 attempts the run ends
  (`FAILED`, Idle). More than 30 tasks in one run: stop.
- Mission blocks (`blocks:` in `catalog.yaml`) run as their own linked Burr run (chain).
- `llm_approval`: every new plan waits for `task_manager/approve_plan` (Lichtblick button).
- Every decision is logged (prompt version, model, input, answers, plan, result) to
  `GEORG_DECISION_LOG_DIR` and can be replayed: `tests/decision_replay/replay.py --decisions <log>`.
- The current plan is on `task_manager/plan` (`std_msgs/String`, JSON) for Lichtblick.
- Profile `real`: LLM modes are refused unless `GEORG_LLM_REAL_APPROVED=1`.

### Add a new task

1. Write the class in `task_manager/tasks/`, derived from `BaseTask`, with
   `async def run(self, robot, state) -> bool` (see `Gesture.py`).
2. Add one entry to `task_manager/catalog/catalog.yaml`: `class` (`module:Class`),
   `action`, `type`, `args_schema` (the constructor arguments), `timeout_s`, `modes`.
   **Tasks that are not in the catalog are rejected at mission start.** The catalog name plus
   the `name_arg` argument become the node name in the Burr graph (e.g. `gesture_look_at`),
   no Burr code needed.
3. Run the tests (see below). `test_validator.py` checks that every catalog class can be imported.

### Add a new mission

1. Copy `task_manager/missions/DigitalFestival.py`; `get_mission()` returns the list of tasks.
2. Register it in `MISSIONS` in `task_manager/missions/__init__.py`.
3. Start it: Lichtblick panel or `task_manager/start` with its id.

### Burr UI

Every mission run gets its own `burr_app_id` and shows up with all steps and states in the
Burr UI: <http://localhost:7241> (service `burr_ui`, started with every profile).
Project `task_manager`, partition key = mission id.
Tracking is switched off with `GEORG_BURR_TRACKING=0`.

### Tests without ROS

```bash
cd task_manager_pkg
pip install "apache-burr[tracking]==0.43.0" pyyaml pytest
python -m pytest test/test_burr_app.py test/test_validator.py
```

ROS message modules are replaced by stand-ins in `test/conftest.py` if they are not installed.

### Priorities

Tasks run in sequence; the priority decides what happens when a task fails:

- **LOW**: discarded after the first try.
- **MID**: retried once after the next task; a second failure discards it.
- **HIGH**: retried up to three more times, then discarded.
- **CRITICAL**: like HIGH, but the mission stops when the retries are used up.
