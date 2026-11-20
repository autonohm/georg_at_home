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
        'robot_namespace', default_value=os.getenv('EDU_ROBOT_NAMESPACE', default='georg')
    )

    # Navigation -> packages/pkg_navigation/config/navigation.launch.py
    # Gestures   -> packages/pkg_gestures/config/gestures.launch.py

    # Listening / Speech
    # stays here until the state of pkg_speech is clear (OPEN_QUESTIONS Q1)

    voice_module = Node(
        package="voice_assistant",
        executable="listen_action_server",
        name="listen_action_server",
        output="screen",
    )

    # Task Manager
    # Runs missions with Burr (P1). The py_trees variant was removed.

    task_manager_module = Node(
        package="georg_task_manager",
        executable="task_manager",
        name="task_manager",
        output="screen",
    )

    return LaunchDescription([
        robot_namespace_arg,
        GroupAction(
            actions=[
                PushRosNamespace(robot_namespace),
                voice_module,
                task_manager_module,
            ]
        )
    ])
