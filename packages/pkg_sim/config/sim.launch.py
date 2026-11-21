import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace


def generate_launch_description():
    robot_namespace = LaunchConfiguration('robot_namespace')
    map_file = LaunchConfiguration('map_file')
    return LaunchDescription([
        DeclareLaunchArgument(
            'robot_namespace', default_value=os.getenv('EDU_ROBOT_NAMESPACE', default='')),
        DeclareLaunchArgument(
            'map_file', default_value=os.path.join(
                os.getenv('GEORG_MAP_DIR', '/root/georg_maps'), 'Nav_Test.yaml')),
        GroupAction(actions=[
            PushRosNamespace(robot_namespace),
            Node(package='georg_sim', executable='sim2d', name='georg_sim', output='screen',
                 parameters=[{'map_file': map_file}]),
        ]),
    ])
