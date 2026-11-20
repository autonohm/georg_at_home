import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace


def generate_launch_description():
    robot_namespace = LaunchConfiguration('robot_namespace')
    robot_namespace_arg = DeclareLaunchArgument(
        'robot_namespace', default_value=os.getenv('EDU_ROBOT_NAMESPACE', default='georg')
    )

    gate = Node(
        package="command_gate",
        executable="command_gate",
        name="command_gate",
        output="screen",
    )

    return LaunchDescription([
        robot_namespace_arg,
        GroupAction(actions=[PushRosNamespace(robot_namespace), gate]),
    ])
