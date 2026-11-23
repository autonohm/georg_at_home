# Operations

How to set up, start, watch and test Georg. Overview of the system: [../README.md](../README.md).

## Machines

| Machine | Role | `/etc/georg/mode` |
| --- | --- | --- |
| Jetson Thor on Georg | the robot: profile `real` (or `sim`/`mock` for tests) | `real` |
| Jetson / PC without robot | development, simulation | `sim` (or none) |
| Mac (without Docker) | quick development with pixi: `dev/macos/README.md` | – |

## Set up

```bash
mkdir -p ~/app && cd ~/app
git clone https://github.com/autonohm/georg_at_home.git && cd georg_at_home
system-files/setup-robot.sh     # on the robot: udev rules, mode file 'real', systemd unit
system-files/setup-PC.sh        # on a development machine: mode file 'sim', Lichtblick, Burr UI
```

Needs Docker with the compose plugin (`docker compose version`) and about 40 GB of disk.
`setup-robot.sh` enables `georg.service`, which runs `projectctl.bash up real` at boot: Georg
comes up idle, no mission starts by itself.

## Build and run

```bash
./projectctl.bash build [profile]          # base image + images (all, or one profile)
./projectctl.bash up mock|sim|real|mcap    # start a profile
./projectctl.bash status                   # containers, health
./projectctl.bash logs <service>           # follow logs, e.g. task_manager
./projectctl.bash down
```

`up real` is refused unless the mode file says `real` and `python3 tools/hardware_scan.py
--check` is clean (report: `docs/hardware_access_report.md`).

### Switches (environment variables for `projectctl.bash up`)

| Variable | Default | Effect |
| --- | --- | --- |
| `GEORG_MAP` | `Nav_Test.yaml` | world/map in `pkg_slam/maps`: `Nav_Test.yaml` (test map), `Wohnung.yaml`, `Arena.yaml` (apartment like the RoboCup@Home arena), `Arena_AtHome.yaml` (converted arena, needs the USD) |
| `GEORG_SIMULATOR` | `sim2d` | `simmj` = MuJoCo physics |
| `GEORG_SIM_LIDARS` | `robot` | `robot` = two TiM571 like on Georg, `center` = one ideal 360° lidar |
| `GEORG_SIM_LIDAR_NOISE` | `0.02` | range noise of the simulated lidars (m) |
| `GEORG_SIM_ODOM_NOISE` | `0` | velocity noise of the wheel odometry (drift) |
| `GEORG_SIM_CMD_LATENCY` | `0` | command latency of the simulated base (s) |
| `GEORG_SIM_DOMAIN_ID` | `30` | ROS domain of mock/sim/mcap (`real` is always 0) |
| `GEORG_WITH_PIB_BACKEND` | `0` | `1`: start `pib_bridge` (sim/real), needs pib-backend running |
| `PIB_SAY_JOIN` | `true` | `false`: do not wait until spoken (machine without loudspeaker) |
| `PIB_POSE_ENABLE` | `0` | `real`: `1` sends named poses (`pib_pose`) to the real servos; otherwise dry run (logged only) |
| `PIB_DOORBELL_TOPIC` | – | `std_msgs/Bool` topic used as doorbell for `Listening(DOORBELL)` |
| `GEORG_WITH_LLM` | `0` | `1`: local LLM server for the planner (`pkg_llm`) |
| `GEORG_MCAP_FILE` | – | profile `mcap`: recording below `recordings/` to replay |

Example: `GEORG_MAP=Arena.yaml GEORG_WITH_PIB_BACKEND=1 ./projectctl.bash up sim`

## Watch

| What | Where |
| --- | --- |
| Lichtblick 1.30 | *Foxglove WebSocket* `ws://<host>:8765`; layout `packages/pkg_viz/lichtblick_layouts/georg_sim.json`; panel: `cd packages/pkg_viz/lichtblick_panel && python3 build.py`, install the `.foxe` |
| Burr UI (every mission run) | `http://<host>:7241` |
| Cerebra (pib-backend) | `http://<host>/` |

Over SSH (e.g. VS Code Remote): forward ports 8765, 7241, 80 and use `localhost`.

Lichtblick settings the layout already sets: 3D panel → Scene → *Mesh up axis* = Z-up, *Ignore
COLLADA up_axis* on; the robot model is the custom URDF layer
`/georg_full/robot_description` (Georg + movable pib). Head camera: image panel
`/oak/rgb/image_raw/compressed` (simulated in `sim`, real in `real`, recorded in `mcap`).

## Missions

Start/abort in the Lichtblick panel, or:

```bash
docker exec georg-task_manager-1 bash -c 'source /ws/install/setup.bash && \
  ros2 service call /task_manager/start georg_task_manager_msgs/srv/StartMission "{mission_id: sim_seat}"'
```

| Mission | Profile | What |
| --- | --- | --- |
| `mock_test` | mock | every package once, against mocks |
| `sim_seat`, `sim_door` | sim (Nav_Test) | drive to the seat / door |
| `sim_gestures` | sim | wave, drive, point, greet (named poses, fake motors) |
| `arena_tour` | sim (Arena/Wohnung) | through all rooms, greet the people |
| `sim_reset` | sim | robot back to the start, empty map |
| `greeting` | any | introduce, ask the name, listen, answer with the name |
| `digital_festival` | real | the event mission |

Named pib poses (`ruhe`, `winken`, `zeigen`, `begruessen`, head `kopf_links`/`kopf_rechts`/`kopf_hoch`/`kopf_runter`/`umschauen` – the head camera follows):
`packages/pkg_pib_model/config/pib_poses.yaml`, limits for the real servos in `pib_limits.yaml` (edit without rebuilding, restart `pib_model` / `pib_bridge`).

## Test

| Level | Command | Needs |
| --- | --- | --- |
| Unit (task manager) | `docker run --rm -v $PWD:$PWD -w $PWD/packages/pkg_task_manager/task_manager_pkg task_manager bash -c 'source /ws/install/setup.bash && python3 -m pytest -q test/test_burr_app.py test/test_validator.py test/test_planner.py test/test_greeting.py'` | image |
| ROS integration (mocks, LLM) | same with `-e GEORG_ROS_TESTS=1` and `test/test_ros_integration.py test/test_llm_integration.py` | image |
| Stack acceptance | `tests/stack/run.sh mock` / `tests/stack/run.sh sim` | running stack |
| Meshes for Lichtblick | `python3 tests/stack/mesh_check.py` | running sim/real stack |
| pib-backend bridge | `tests/stack/bridge_check.py` (see its header) | sim + bridge + pib-backend |
| Operation (compose, units) | `python3 -m pytest tests/system` | Docker |
| Decision replay (LLM) | `tests/decision_replay/` | – |
| pib model, worlds | `cd packages/pkg_pib_model/pib_model_pkg && python3 -m pytest test`; `python3 -m pytest packages/pkg_sim/test` | – |

## Record and replay

The `recorder` service records mission status, sensors, pib joint states, head camera and
detections to `recordings/` (MCAP, one file per hour). Replay what the robot saw:

```bash
GEORG_MCAP_FILE=<folder or file below recordings/> ./projectctl.bash up mcap
```

SLAM rebuilds the map from the recording; Lichtblick can also open the `.mcap` directly.

## Worlds for the simulation

| Map | Made by |
| --- | --- |
| `Nav_Test.yaml` | navigation team (hand-drawn test map) |
| `Wohnung.yaml` (+ `_visuals.xml`) | `python3 packages/pkg_sim/tools/build_world.py` |
| `Arena.yaml` (+ `_visuals.xml`) | `python3 packages/pkg_sim/tools/build_arena.py` |
| `Arena_AtHome.yaml` | `packages/pkg_sim/tools/arena_convert.py` from the RoboCup@Home USD (not in git, see `packages/pkg_sim/assets/README.md`) |

A map gives everything the same geometry: obstacle polygons (navigation, lidar, physics), named
places (navigation targets) and the start (`type: sim_start`); `<map>_visuals.xml` is what the
simulated camera renders.

## Network on the robot

All containers of Georg, pib-backend and Cerebra share the Docker network `pib-network`; the ROS
domain alone separates simulation (30) from the robot (0) – see DECISIONS "One network, domains
separate".

This works as long as pib-backend runs **on the same machine** (the Jetson). That is the target.
If pib-backend runs on the **Raspberry Pi** (192.168.2.1) instead: ROS 2 finds partners by
multicast, and multicast does not leave a Docker bridge network, so the containers on the Jetson
would not see pib-backend on the Pi although both are in the same LAN (192.168.2.0/24) and the same
domain. Fix, only for that setup: let Georg's containers use the LAN directly – either
`network_mode: host` (simplest, usual for ROS on robots) or a `macvlan` network with fixed
addresses `192.168.2.51-80` (the plan in the README). This is a compose setting only, no code
change; the domains keep the simulation separate as before.

## Troubleshooting

| Symptom | Cause / fix |
| --- | --- |
| `up real` refused | mode file not `real`, or hardware scan finds problems (`docs/hardware_access_report.md`) |
| `StartMission` rejected: action server not reachable | that package is not running: `projectctl.bash status`, its logs |
| Lichtblick does not connect | use Lichtblick 1.30 (`foxglove_bridge` 3.x speaks only `foxglove.sdk.v1`) |
| Robot model tipped over in Lichtblick | 3D panel → Scene → Mesh up axis = Z-up, Ignore COLLADA up_axis |
| Panel calls `/georg/task_manager/...` | old panel version or setting: clear "Robot namespace" in the panel settings |
| Nothing on `ros2 topic list` on the host | the stack runs in domain 30: `export ROS_DOMAIN_ID=30`, or use `docker exec` |
| Robot does not drive | chain `cmd_vel/nav → twist_mux → twist_limiter → cmd_vel → driver/simulator`; check each with `ros2 topic hz` |
| Speech hangs on a machine without loudspeaker | `PIB_SAY_JOIN=false`; restart `pib-backend-ros-voice-assistant-1` |
