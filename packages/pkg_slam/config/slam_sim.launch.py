"""SLAM in profile sim (P3): slam_toolbox only.

The simulator (pkg_sim) publishes merged_scan, odom and the tf odom -> base_footprint,
so the lidar drivers, the scan merger and rf2o laser odometry are not needed.
Run from this folder (parameters are relative): ros2 launch slam_sim.launch.py
"""
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import PushRosNamespace
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    robot_namespace = LaunchConfiguration('robot_namespace')
    slam_launch = PathJoinSubstitution(
        [FindPackageShare('slam_toolbox'), 'launch', 'online_async_launch.py'])
    slam_toolbox = IncludeLaunchDescription(
        slam_launch,
        launch_arguments={
            'autostart': 'true',
            'use_lifecycle_manager': 'false',
            'slam_params_file': PathJoinSubstitution(['.', 'parameters', 'slam_toolbox.yaml']),
            'use_sim_time': 'false',
        }.items(),
    )
    return LaunchDescription([
        DeclareLaunchArgument('robot_namespace', default_value='georg'),
        GroupAction(actions=[PushRosNamespace(robot_namespace), slam_toolbox]),
    ])
