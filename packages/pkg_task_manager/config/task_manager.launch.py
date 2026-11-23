import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node

from launch.actions import GroupAction
from launch_ros.actions import PushRosNamespace


def generate_launch_description():

    # robot namespace
    robot_namespace = LaunchConfiguration('robot_namespace')
    robot_namespace_arg = DeclareLaunchArgument(
        'robot_namespace', default_value=os.getenv('EDU_ROBOT_NAMESPACE', default='')
    )

    # Navigation -> packages/pkg_nav2/config/nav2.launch.py (Nav2)
    # Gestures   -> packages/pkg_gestures/config/gestures.launch.py

    # Listening / Speech: the Listen action server (audio/listen) is not started here any more;
    # pib-audio was removed (2026-11-21); speech now goes through pkg_pib_bridge

    # Task Manager
    # Runs missions with Burr (P1). The py_trees variant was removed.

    task_manager_module = Node(
        package="task_manager",
        executable="task_manager",
        name="task_manager",
        output="screen",
    )

    return LaunchDescription([
        robot_namespace_arg,
        GroupAction(
            actions=[
                PushRosNamespace(robot_namespace),
                task_manager_module,
            ]
        )
    ])
