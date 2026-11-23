# Decisions

Why the stack is built the way it is. Newest first. Each: decision – why – consequence.

## Simulation and visualisation

**Own apartment worlds instead of converting the arena USD** (2026-11-21).
The converted RoboCup@Home USD gave open rooms and doorways closed by frame posts.
`build_world.py` (`Wohnung.yaml`) and `build_arena.py` (`Arena.yaml`) generate closed rooms
(2.4 m walls, 0.9–1.0 m doors, ceiling, lights), furniture and people from primitives; every
place is checked free and reachable. The converter (`arena_convert.py`) stays as an option; its
meshes are not in git.

**One map file drives everything** (`GEORG_MAP`). Navigation, simulated lidar, MuJoCo physics,
camera and missions read the same YAML; the camera adds `<map>_visuals.xml`. Places are free
standing spots, so `arena_tour` drives there without stand-off.

**Simulated head camera** (MuJoCo, EGL on the GPU). Same topic, type, frame and rate as the
real OAK camera of pib-backend (`/oak/rgb/image_raw/compressed`, `oak_rgb_camera_optical_frame`,
10 Hz). The camera frame sits on the pib head (`pib_model`), so the image follows the head in sim
and on the robot.

**No sensor data across domains.** `pib_bridge` forwards nothing from pib-backend into the
stack: in sim the robot sees only the simulation, like it can only move simulated motors. On the
robot both share domain 0; in `mcap` the recording plays (the recorder records camera, detections
and joint states).

**Movable pib from the pib-3d web model** (the one Cerebra shows, `v0.11.6`, loaded at image
build, not in git). Converted to a URDF; joint angles converted from pib-backend motor values with
Cerebra's formula. The rigid pib of `georg_description` is hidden in the combined description
`/georg_full/robot_description`. Lichtblick turns GLB by +90° about x (its *Mesh up axis* setting
does not apply to GLB) → the URDF counter-rotates the pib meshes; STL/OBJ need Z-up in the layout.

**Mount of pib on Georg** estimated from the bounding boxes of the rigid pib mesh
(`pib_model` parameters `mount_xyz`, `mount_rpy`); confirmed visually.

**Sam's `sim_mode` only for the drive chain in sim.** `drive` runs `twist_mux` + `twist_limiter`
without the driver, so sim has the robot's command chain. SLAM/odometry stay with the simulator
because the map YAML places are in the simulator's odom frame. Now that Nav2 drives on the
SLAM map, the simulator could publish wheel odometry only and run rf2o/SLAM like on the robot
(OPEN_ISSUES N8).

**Realistic sensors in sim:** two TiM571 at the URDF poses (270°, noise), merged like the
scan merger; optional odometry drift and command latency; `/clock`. Simulator subscribes
`cmd_vel` best effort (the twist limiter publishes best effort).

**Reset and gestures in sim:** mission `sim_reset` (start pose, empty map); task `pib_pose` with
named poses (`pib_poses.yaml`) – in sim the fake motors execute it, on the robot `pib_bridge` will
send it to pib-backend `/apply_joint_trajectory` with joint limits (OPEN_ISSUES G1).

## Speech (pib-backend)

**A bridge with a fixed allowlist instead of changing the task manager** (`pkg_pib_bridge`).
One process in two ROS domains; the task manager keeps its actions (`speech/say`,
`audio/listen`), the bridge maps them to pib-backend (`/play_audio_from_speech`,
`/record_audio`). Only this container joins pib-backend's Docker network. Optional
(`GEORG_WITH_PIB_BACKEND=1`).

**Speak as an action, not a service call** – so catalog, start check, mocks and cancel work like
for every task. Ported from branch `pib_backend_integration` (leakmpf): `Speak` with text from
the state, `Listening` via `/record_audio`, mission `greeting` with `extract_name`.

**Our message package `datatypes` renamed to `georg_speech_msgs`** – pib-backend has a different
package of the same name; the base image builds pib-backend's `datatypes` (pinned commit).

## Safety and operation

**One network, domains separate** (2026-11-23). All Georg containers join the Docker network
`pib-network` that pib-backend and Cerebra already share (fixed name in every compose file).
ROS 2 nodes can therefore always reach each other on the network; **only the ROS domain**
separates them: `real` = 0 like pib-backend, `mock`/`sim`/`mcap` = 30. Before, a second barrier
(our own network `georg_pib-network`) also cut Georg off from pib-backend in `real`, so poses,
gestures, speech and the real joint states could never arrive there. Checked: in `sim`,
pib-backend (domain 0) sees none of our topics; the stack (domain 30) sees none of
pib-backend's; `pib_bridge` still connects the two for speech on purpose.
If pib-backend runs on the Raspberry Pi instead of the Jetson, see OPERATIONS "Network on the
robot".

**No command gate; `ROS_DOMAIN_ID` per profile** (`real` 0 like pib-backend, else 30). The gate
only repeated what profiles, `sim_mode` and the `up real` check already guarantee, and was always
open in `real`; separate domains close the real gap (a sim on the same network).

**No robot namespace** (as on `main`). All topics/services at root (`/task_manager/start`).
Healthchecks assume no namespace.

**Profiles `mock` / `sim` / `real` / `mcap`** select the containers; `projectctl.bash` sets
`GEORG_PROFILE`, `GEORG_SIM_MODE` (only from the profile) and `ROS_DOMAIN_ID`.

**Acceptance against the running stack** (`tests/stack/`) instead of one test image with all
packages: tests exactly what runs on the robot.

**`pib-sdk` not installed in the gesture image** – unused (imports commented out), drives servos
past the stack, and conflicts with ROS Jazzy's numpy on arm64.

## Navigation

**Nav2 on the live SLAM map** (2026-11-23, `pkg_nav2`). The own A* + route driver got stuck at
door corners and had no localisation (OPEN_ISSUES N1–N5). Nav2 (Jazzy) uses the map and the
`map -> odom` of slam_toolbox, so no map server and no AMCL. MPPI with the `Omni` motion model
(mecanum, no preferred direction), footprint 0.50 × 0.42 m, speeds below the twist_limiter.
Output goes through the collision monitor to `cmd_vel/nav`, so twist_mux and the twist_limiter
of `pkg_drive` stay in charge and teleop keeps priority. Only the needed Nav2 nodes are started
(own launch file), the parameters are generated from the nav2_bringup defaults and list every
change. The task manager keeps its tasks: `NavigateObject` looks up the place in the map YAML
and sends `navigate_to_pose`. Started from Sam's branch `pkg_nav2`.

**`pkg_navigation` removed from this branch** (2026-11-23, user decision) after Nav2 drove the
Arena tour 7/7 in sim. Nav2 is the only navigation; there is no `GEORG_NAV_BACKEND` switch any
more. `main` keeps `pkg_navigation`; `georg_nav_msgs` (`Navigate`, `DriveRoute`) stays in
`pkg_interfaces` but is unused here.

## Task manager (P0–P8, 2026-11-20)

- Burr replaces the sequential task manager and py_trees; one Burr run per mission; missions as
  chains, LLM planning as a star graph.
- Task catalog (`catalog.yaml`) is the contract between task manager, packages and LLM; a
  validator checks plans; tasks are allowed per profile.
- LLM planner (OpenAI-compatible, `pkg_llm`) with modes mission / llm / llm + approval; LLM
  modes on `real` only with `GEORG_LLM_REAL_APPROVED=1`.
- Lichtblick (1.30) is the operator UI: own panel (plain JS), `foxglove_bridge`.
- Folder rule: `pkg_<area>/<package>_pkg/<package>/`, one container per package, shared
  interfaces in `pkg_interfaces`.
