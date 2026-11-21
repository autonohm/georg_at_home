import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, GroupAction
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace


def generate_launch_description():
    # Nodes moved 1:1 from pkg_task_manager/config/task_manager.launch.py (P0).
    robot_namespace = LaunchConfiguration('robot_namespace')
    robot_namespace_arg = DeclareLaunchArgument(
        'robot_namespace', default_value=os.getenv('EDU_ROBOT_NAMESPACE', default='')
    )

    # One planning server per action name the task manager calls (robot.py):
    # nav/navigate_object_x (NavigateObject) and nav/navigate_room_x (NavigateRoom).
    # Relative names, so they end up in the robot namespace (e.g. /nav/... or /georg/nav/...).
    nav_object = Node(
        package='navigate_server',
        executable='navigate_action_server',
        name='nav_object_server',
        arguments=['--node-name', 'nav_object_server',
                   '--action-name', 'nav/navigate_object_x'],
        output='screen',
    )

    nav_room = Node(
        package='navigate_server',
        executable='navigate_action_server',
        name='nav_room_server',
        arguments=['--node-name', 'nav_room_server',
                   '--action-name', 'nav/navigate_room_x'],
        output='screen',
    )

    # Profiles real and sim: drive commands go through twist_mux (input cmd_vel/nav) and the
    # twist_limiter of pkg_drive, then to the driver (real) or the simulator (sim, sim_mode
    # of pkg_drive). Without pkg_drive (mock, the Mac stack) directly on cmd_vel.
    real = os.environ.get('GEORG_PROFILE') in ('real', 'sim')
    drive_route_module = Node(
        package='drive_route_server',
        executable='drive_route_action_server',
        name='drive_route_action_server',
        remappings=[('cmd_vel', 'cmd_vel/nav')] if real else [],
        output='screen',
    )

    return LaunchDescription([
        robot_namespace_arg,
        GroupAction(actions=[
            PushRosNamespace(robot_namespace),
            nav_object,
            nav_room,
            drive_route_module,
        ]),
    ])
