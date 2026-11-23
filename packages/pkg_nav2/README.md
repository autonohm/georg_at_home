# pkg_nav2

[Nav2](https://docs.nav2.org/) (ROS 2 Jazzy) for Georg: drives to a pose on the live SLAM map.
Successor of `pkg_navigation` (own A* + drive route server, removed from this branch, still on
`main`), which got stuck at door corners (docs/OPEN_ISSUES.md N3).

Started from Sam's branch `pkg_nav2` (Dockerfile, default parameters) and set up for Georg.

## How it fits in

| Needs | From |
|-------|------|
| `/map`, TF `map -> odom` | slam_toolbox (`pkg_slam`) |
| TF `odom -> base_footprint`, `/odom` | robot drive / simulator (`pkg_sim`) |
| `/merged_scan` | laser_scan_merger (`pkg_slam`) / simulator |

Output: `cmd_vel/nav` → twist_mux → twist_limiter (`pkg_drive`) → motors. Teleop keeps the higher
priority in twist_mux.

```
controller/behaviors -> cmd_vel_nav -> velocity_smoother -> collision_monitor -> cmd_vel/nav
```

No `map_server` and no AMCL: SLAM localizes and maps at the same time.

## Files

- `config/nav2.launch.py` – the Nav2 nodes Georg needs (controller, planner, smoother,
  behaviors, velocity smoother, collision monitor, BT navigator) plus the lifecycle manager.
- `config/nav2_params.yaml` – generated from the nav2_bringup defaults; the header lists every
  change (mecanum/Omni MPPI, footprint 0.50 × 0.42 m, speeds below the twist_limiter, frames).

## Try it

```bash
./projectctl.bash up sim
# goal in the map frame (the sim map frame = the frame of the map YAML at the start)
ros2 action send_goal /navigate_to_pose nav2_msgs/action/NavigateToPose \
  "{pose: {header: {frame_id: map}, pose: {position: {x: 5.0, y: 3.0}, orientation: {w: 1.0}}}}"
```

In Lichtblick: costmaps `/global_costmap/costmap`, `/local_costmap/costmap`, path `/plan`.

## Notes

- Place names from the map YAML are map poses only in the simulation (SLAM starts at the
  `sim_start` of the YAML). On the robot the SLAM map frame starts where Georg was switched on;
  places need a saved SLAM map with places in it (docs/OPEN_ISSUES.md S10).
