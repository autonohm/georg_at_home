# pkg_navigation

Navigation package for the pib robot "Georg". It provides two ROS 2 action servers and the shared action definitions:

- **Navigate server** (`navigate_server`): plans a collision-free path on a map with A\* and returns waypoints. It does not move the robot.
- **Drive route server** (`drive_route_server`): follows a list of waypoints with a mecanum controller, using odometry and publishing velocity commands.
- **`georg_nav_msgs`**: the `Navigate` and `DriveRoute` action definitions. They live in [../pkg_interfaces/georg_nav_msgs/](../pkg_interfaces/georg_nav_msgs/) and are built into the base image.

The mainly used flow is: plan with `Navigate`, then drive the returned waypoints with `DriveRoute`. The Task Manager does this in `NavigateObject`.

## Package layout

```
pkg_navigation/
├── Dockerfile, docker-compose.yaml # own container (profiles sim, real)
├── config/navigation.launch.py
├── navigate_server_pkg/            # Planning server (ament_python)
│   └── navigate_server/
│       ├── navigate_action_server.py   # ROS 2 action server
│       ├── grid_rasterizer.py          # YAML map -> occupancy grid
│       └── astar.py                    # A* search and path simplification
└── drive_route_server_pkg/         # Driving server (ament_python)
    └── drive_route_server/
        ├── drive_route_action_server.py   # ROS 2 action server
        ├── mecanum_controller.py          # waypoint controller
        └── drive_route_client.py          # client example
```

The map files are in [../pkg_slam/maps/](../pkg_slam/maps/) and are mounted at `/root/georg_maps`. See [maps/README.md](../pkg_slam/maps/README.md) for the format.

## Actions

### `/nav/navigate_room_x` and `/nav/navigate_object_x` (Navigate)

`pkg_interfaces/georg_nav_msgs/action/Navigate.action`:

```
geometry_msgs/Point start
geometry_msgs/Point goal
string map_name          # map YAML file name or absolute path; empty = default map
bool simplify_path
---
int8 result_code         # RESULT_OK=0, RESULT_NO_PATH_FOUND=1, RESULT_START_BLOCKED=2,
                         # RESULT_GOAL_BLOCKED=3, RESULT_MAP_NOT_LOADED=4, RESULT_ABORTED=5
geometry_msgs/Point[] waypoints
float32 path_length_m
---
int32 cells_expanded     # feedback during the A* search
```

Coordinates are in meters in the map frame. Start and goal must lie in free cells.

### `/nav/drive_route` (DriveRoute)

`pkg_interfaces/georg_nav_msgs/action/DriveRoute.action`:

```
geometry_msgs/Point[] waypoints
float32 max_speed        # max strafe speed in m/s; 0.0 = server default
---
int8 result_code         # RESULT_OK=0, RESULT_OBSTACLE_DETECTED=1, RESULT_ABORTED=2, RESULT_TIMEOUT=3
---
int32 current_waypoint_index
geometry_msgs/Point current_position
```

The drive server subscribes to `odom` (`nav_msgs/Odometry`) and publishes `cmd_vel` (`geometry_msgs/Twist`). It waits up to 5 s for the first odometry message before it starts.

## Build

```bash
colcon build --packages-select georg_nav_msgs navigate_server drive_route_server
source install/setup.bash
```

`georg_nav_msgs` must be built first. The Docker image builds the whole workspace.

## Running the servers

### Navigate server (room and object planning)

Two instances run side by side, one per action name:

```bash
source install/setup.bash

ros2 run navigate_server navigate_action_server \
  --node-name nav_room_server \
  --action-name /nav/navigate_room_x

ros2 run navigate_server navigate_action_server \
  --node-name nav_object_server \
  --action-name /nav/navigate_object_x
```

Optional parameters:

```bash
ros2 run navigate_server navigate_action_server --ros-args \
  -p map_dir:=/home/<user>/georg_maps \
  -p default_map_name:=Nav_Test.yaml \
  -p cell_size_m:=0.05 \
  -p robot_radius_m:=0.0
```

| Parameter | Default | Purpose |
|---|---|---|
| `map_dir` | `GEORG_MAP_DIR` or `root/georg_maps` | Folder with map YAML files |
| `default_map_name` | `GEORG_DEFAULT_MAP` or `Nav_Test.yaml` | Map used when a goal does not name one |
| `cell_size_m` | `0.05` | Grid cell size |
| `robot_radius_m` | `0.0` | Inflates obstacles by this radius for clearance |

Maps are cached per server after the first load.

### Drive route server

```bash
source install/setup.bash
ros2 run drive_route_server drive_route_action_server
```

Optional parameters:

```bash
ros2 run drive_route_server drive_route_action_server --ros-args \
  -p max_linear_speed:=0.4 \
  -p max_angular_speed:=1.5 \
  -p k_linear:=1.0 \
  -p k_angular:=2.0 \
  -p waypoint_tolerance_m:=0.1 \
  -p final_position_tolerance_m:=0.03 \
  -p final_heading_tolerance_rad:=0.15
```

### Robot launch

`config/navigation.launch.py` starts the navigate server and the drive server under the robot namespace (`georg` by default).

## Typical use: plan, then drive

```python
# 1. plan
nav_goal = Navigate.Goal()
nav_goal.start = Point(x=start_x, y=start_y, z=0.0)
nav_goal.goal = Point(x=goal_x, y=goal_y, z=0.0)
nav_goal.map_name = "/root/georg_maps/Nav_Test.yaml"
nav_goal.simplify_path = True
# send to /nav/navigate_object_x, check result.result_code == RESULT_OK

# 2. drive
drive_goal = DriveRoute.Goal()
drive_goal.waypoints = nav_result.waypoints
# send to /nav/drive_route, check result.result_code == RESULT_OK
```

`NavigateRoom` and `NavigateObject` in `pkg_task_manager/task_manager_pkg/task_manager/tasks/` implement this pattern.

## How to add a new navigation action

Example: a `NavigateZone` action that plans to a named zone.

1. **Define the action** in `pkg_interfaces/georg_nav_msgs/action/NavigateZone.action`, and add it to `pkg_interfaces/georg_nav_msgs/CMakeLists.txt` in `rosidl_generate_interfaces`. Rebuild `georg_nav_msgs`.
2. **Write the server.** Copy `navigate_action_server.py` and change the action type and the goal handling. Reuse `grid_rasterizer.load_grid` and `astar.find_path` for the planning logic. Give it its own node and action names. Keep the `ReentrantCallbackGroup` and `MultiThreadedExecutor` pattern if the server needs concurrent callbacks.
3. **Register the executable** in `navigate_server_pkg/setup.py` under `console_scripts`.
4. **Add it to the launch file** in `config/navigation.launch.py`, as a `Node` inside the `GroupAction`.
5. **Add a task** in `pkg_task_manager/task_manager_pkg/task_manager/tasks/`, following `NavigateObject.py`, and add the client to `task_manager/robot.py`.
6. **Build and test** on the robot or in simulation before adding it to a mission.

For a driving action, follow `drive_route_action_server.py`. The controller parameters come from `ControllerGains` in `mecanum_controller.py`.

## Known issues

- **Namespace mismatch risk.** The examples above use absolute action names (`/nav/...`). The launch file uses relative names (`nav/...`). Under the robot namespace, absolute names are not namespaced, so the client and server may not find each other. Use the relative names (`nav/navigate_room_x`) in both places.
- **`fake_odom` entry point is missing.** `navigate_server_pkg/setup.py` declares `fake_odom = navigate_server.odom_sim:main`, but there is no `odom_sim.py` in the package. Running `ros2 run navigate_server fake_odom` will fail until the module is added or the entry point is removed.
- **Default map directory.** `DEFAULT_MAP_DIR` falls back to the relative path `root/georg_maps` when `GEORG_MAP_DIR` is not set. Set `map_dir` or `GEORG_MAP_DIR` explicitly.
- **`RESULT_OBSTACLE_DETECTED` is never returned.** The drive server defines the code, but nothing sets it. The drive server has no obstacle detection yet.
- **Uncommitted changes.** `grid_rasterizer.py` and `navigate_action_server.py` have local modifications that are not committed. Check `git status` before relying on the behavior described here.

## Troubleshooting

- **`Map not loaded/found`:** the map file does not exist under `map_dir`. Check the file name and the `map_dir` parameter.
- **`Start/Goal position ... is in an occupied/out-of-bounds cell`:** the point is inside a wall, an obstacle, or outside the boundary. Pick a point in free space, or increase `cell_size_m` resolution if the point is close to a wall.
- **`A* found no path`:** the goal is enclosed or blocked. Check the map.
- **Drive server aborts at start:** no odometry message arrived within 5 s. Check that `odom` is published (`ros2 topic echo /odom --once`).
- **Robot drifts or oscillates:** tune `k_linear`, `k_angular`, and the tolerances.
