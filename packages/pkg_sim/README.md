# pkg_sim

Simulator of Georg for compose profile `sim` (plan P3). Headless; look at it in Lichtblick.

| Stage | Executable | What it is |
| --- | --- | --- |
| 1 | `sim2d` | 2D simulator without physics engine. Fast, no dependencies. |
| 2 | `simmj` | MuJoCo: the same interface, physics from MuJoCo (see below). |

Both provide the topics of the real robot, so SLAM, navigation and the task manager run unchanged:

| Topic (namespace `georg`) | Direction | Note |
| --- | --- | --- |
| `cmd_vel` (`Twist`) | in | mecanum: `linear.x`, `linear.y`, `angular.z`; stops after 0.5 s without commands |
| `odom` (`Odometry`) | out | odom frame = map frame of the map YAML |
| `merged_scan`, `scan` (`LaserScan`) | out | 360°, 12 m, frame `base_link` |
| `/tf` `odom -> base_footprint`, `/tf_static` `base_footprint -> base_link` | out | |

The world comes from the map YAML in `pkg_slam/maps` (default `Nav_Test.yaml`): walls and
obstacles block the robot and the laser. A step into a wall is not executed.
The robot radius (0.2 m) must stay below the planner's inflation (0.25 m in `grid_rasterizer.py`).

## Run

```bash
# Docker
./projectctl.bash up sim                         # GEORG_SIMULATOR=simmj for MuJoCo

# Mac without Docker (dev/macos)
pixi run sim                                     # simulator + SLAM + navigation + task manager
ros2 service call /georg/task_manager/start georg_task_manager_msgs/srv/StartMission "{mission_id: sim_seat}"
```

In `sim`, SLAM runs `pkg_slam/config/slam_sim.launch.py` (slam_toolbox only). The map is on `/map`.
Missions for the simulator: `sim_seat` (drive to the seat), `sim_door` (drive to the door).

## Tests

- `georg_sim/test/test_world.py`: walls, raycast, free space (pytest, no ROS)
- `pkg_task_manager/georg_task_manager/test/test_sim_integration.py`: acceptance criteria of P3
  over real ROS (`pixi run test_sim`)
