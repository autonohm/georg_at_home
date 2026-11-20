"""SLAM in profile mcap (P5): slam_toolbox on a replayed recording, simulated time.

The player (ros2 bag play --clock) publishes /clock and the raw sensor data of the
recording (merged_scan, odom, tf without map -> odom, see tools/mcap_raw_only.py).
slam_toolbox builds the map live and publishes map -> odom itself.
Run from this folder (parameters are relative): ros2 launch slam_mcap.launch.py
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
            'use_sim_time': 'true',
        }.items(),
    )
    return LaunchDescription([
        DeclareLaunchArgument('robot_namespace', default_value='georg'),
        GroupAction(actions=[PushRosNamespace(robot_namespace), slam_toolbox]),
    ])
