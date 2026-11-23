"""Nav2 for Georg: navigation on the live SLAM map (no map_server, no AMCL).

slam_toolbox (pkg_slam) provides /map and map -> odom; the simulator or the robot provide
odom -> base_footprint and /merged_scan. Nav2 drives through twist_mux of pkg_drive:

    controller/behaviors -> cmd_vel_nav -> velocity_smoother -> cmd_vel_smoothed
        -> collision_monitor -> cmd_vel/nav -> twist_mux -> twist_limiter -> motors

Only the nodes Georg needs (no route server, docking, waypoint follower), so the parameter
file stays short: nav2_params.yaml next to this file (/config in the container).
"""

import os

from launch import LaunchDescription
from launch_ros.actions import Node

PARAMS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nav2_params.yaml')
NAV_NODES = [
    # (package, executable, node name, remap cmd_vel -> cmd_vel_nav)
    ('nav2_controller', 'controller_server', 'controller_server', True),
    ('nav2_smoother', 'smoother_server', 'smoother_server', False),
    ('nav2_planner', 'planner_server', 'planner_server', False),
    ('nav2_behaviors', 'behavior_server', 'behavior_server', True),
    ('nav2_velocity_smoother', 'velocity_smoother', 'velocity_smoother', True),
    ('nav2_collision_monitor', 'collision_monitor', 'collision_monitor', False),
    ('nav2_bt_navigator', 'bt_navigator', 'bt_navigator', False),
]


def generate_launch_description():
    nodes = []
    for package, executable, name, remap in NAV_NODES:
        remappings = [('cmd_vel', 'cmd_vel_nav')] if remap else []
        nodes.append(Node(package=package, executable=executable, name=name, output='screen',
                          parameters=[PARAMS], remappings=remappings, respawn=True,
                          respawn_delay=2.0))
    nodes.append(Node(
        package='nav2_lifecycle_manager', executable='lifecycle_manager',
        name='lifecycle_manager_navigation', output='screen',
        parameters=[{'autostart': True, 'use_sim_time': False,
                     'node_names': [n[2] for n in NAV_NODES]}]))
    return LaunchDescription(nodes)
