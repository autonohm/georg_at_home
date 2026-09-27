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


    # Navigation

    nav_room_module = Node(
        package="navigate_server",
        executable="navigate_action_server",
        name="nav_room_server",
        arguments=["--node-name", "nav_room_server",
                    "--action-name", "nav/navigate_room_x"],
        output="screen",
    )

    nav_obj_module = Node(
        package="navigate_server",
        executable="navigate_action_server",
        name="nav_object_server",
        arguments=["--node-name", "nav_object_server",
                    "--action-name", "nav/navigate_object_x"],
        output="screen",
    )

    drive_route_module = Node(
        package="drive_route_server",
        executable="drive_route_action_server",
        name="drive_route_action_server",
        output="screen",
    )



    # Gestures

    gesture_module = Node(
        package="pib_gestures_action",
        executable="pib_gestures_server.py",
        name="pib_gestures_server",
        output="screen",
    )




    # Listening / Speech


    voice_module = Node(
        package="voice_assistant",
        executable="listen_action_server",
        name="listen_action_server",
        output="screen",
    )




    # Task Manager

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
                nav_room_module,
                nav_obj_module,
                drive_route_module,
                gesture_module,
                #voice_module,
                task_manager_module
            ]
        )
    ])
