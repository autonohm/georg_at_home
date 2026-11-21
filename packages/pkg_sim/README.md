# pkg_sim

Simulator of Georg for compose profile `sim`. Headless; watch it in Lichtblick. It replaces
the motor driver, the lidars, the head camera and the pib servos – everything else (navigation,
SLAM, drive chain, task manager, gestures) runs unchanged.

| Service / executable | What it is |
| --- | --- |
| `sim` → `sim2d` (default) | 2D simulator without physics engine, fast |
| `sim` → `simmj` (`GEORG_SIMULATOR=simmj`) | MuJoCo 3.16: same interface, contacts and rays from MuJoCo |
| `sim_camera` | head camera rendered with MuJoCo on the GPU (EGL), like the real OAK camera |

## Interface (as on the robot)

| Topic | Dir | Note |
| --- | --- | --- |
| `cmd_vel` (`Twist`, best effort) | in | from `twist_limiter` (Sam's `sim_mode` drive chain); stops after 0.5 s without commands |
| `odom`, `odom/wheel` (`Odometry`) | out | odom frame = map frame of the map YAML; optional drift |
| `lidar1/scan`, `lidar2/scan` | out | two TiM571 at the URDF poses (270°, noise) |
| `merged_scan`, `scan` | out | merged like `laser_scan_merger` (360°, 1°, from 0.3 m, `base_link`) |
| `/tf` `odom → base_footprint`, `/clock` | out | `base_footprint → base_link` and lidar frames come from `georg_description` |
| `/oak/rgb/image_raw/compressed` | out | `sim_camera`, 10 Hz jpeg, frame `oak_rgb_camera_optical_frame` (on the pib head) |
| `sim/ground_truth` | out | true pose, for tests |
| action `sim/reset` (`georg_sim_msgs/ResetSim`) | in | start pose, stopped, odometry reset, optional empty SLAM map (mission `sim_reset`) |

Parameters (compose environment): `GEORG_MAP`, `GEORG_SIM_LIDARS`, `GEORG_SIM_LIDAR_NOISE`,
`GEORG_SIM_ODOM_NOISE`, `GEORG_SIM_CMD_LATENCY` – see [docs/OPERATIONS.md](../../docs/OPERATIONS.md).

## Worlds

The world is a map YAML in `pkg_slam/maps` (`GEORG_MAP`): obstacle polygons block robot, lidar
and planner; objects are navigation places; `type: sim_start` is the start pose. The camera
renders `<map>_visuals.xml` if it exists (else the walls of the map as boxes).

| Map | Generator |
| --- | --- |
| `Nav_Test.yaml` | hand-drawn (navigation team) |
| `Wohnung.yaml` | `tools/build_world.py` |
| `Arena.yaml` | `tools/build_arena.py` (RoboCup@Home-like apartment, 5 rooms, people) |
| `Arena_AtHome.yaml` | `tools/arena_convert.py` from the competition USD (`assets/`, not in git) |

## Tests

- `georg_sim/test/test_world.py`, `test_mjcf.py` (pytest, no ROS); `test/test_arena.py`
- stack: `tests/stack/run.sh sim` (navigation, abort, reset, gestures)
- Mac (pixi): `pixi run test_sim`, `pixi run test_sim_mj`
