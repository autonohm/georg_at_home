import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace


def generate_launch_description():
    # Node moved 1:1 from pkg_task_manager/config/task_manager.launch.py (P0).
    robot_namespace = LaunchConfiguration('robot_namespace')
    robot_namespace_arg = DeclareLaunchArgument(
        'robot_namespace', default_value=os.getenv('EDU_ROBOT_NAMESPACE', default='georg')
    )

    gesture_module = Node(
        package="pib_gestures_action",
        executable="pib_gestures_server.py",
        name="pib_gestures_server",
        output="screen",
    )

    return LaunchDescription([
        robot_namespace_arg,
        GroupAction(actions=[
            PushRosNamespace(robot_namespace),
            gesture_module,
        ]),
    ])
