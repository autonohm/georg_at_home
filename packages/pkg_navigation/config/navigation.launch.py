import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace


def generate_launch_description():
    # Nodes moved 1:1 from pkg_task_manager/config/task_manager.launch.py (P0).
    robot_namespace = LaunchConfiguration('robot_namespace')
    robot_namespace_arg = DeclareLaunchArgument(
        'robot_namespace', default_value=os.getenv('EDU_ROBOT_NAMESPACE', default='georg')
    )

    nav_module = Node(
        package="navigate_server",
        executable="navigate_action_server",
        name="nav_server",
        # TODO(OPEN_QUESTIONS Q12): Task Manager erwartet nav/navigate_object_x und nav/navigate_room_x
        arguments=["--node-name", "nav_server",
                   "--action-name", "/nav/navigate"],
        output="screen",
    )

    drive_route_module = Node(
        package="drive_route_server",
        executable="drive_route_action_server",
        name="drive_route_action_server",
        output="screen",
    )

    return LaunchDescription([
        robot_namespace_arg,
        GroupAction(actions=[
            PushRosNamespace(robot_namespace),
            nav_module,
            drive_route_module,
        ]),
    ])
