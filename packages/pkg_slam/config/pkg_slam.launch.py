from launch import LaunchDescription

from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch.actions import IncludeLaunchDescription
from launch.substitutions import EnvironmentVariable, PathJoinSubstitution

from launch.actions import GroupAction
from launch_ros.actions import PushRosNamespace

from launch.conditions import IfCondition, UnlessCondition
from launch.actions import LogInfo


def generate_launch_description():
    robot_namespace = LaunchConfiguration('robot_namespace')
    sim_mode = LaunchConfiguration('sim_mode')


    slam = IncludeLaunchDescription(
        'slam.launch.py',
    )

    lidars = IncludeLaunchDescription(
        'lidars.launch.py',
        condition=UnlessCondition(sim_mode),
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'robot_namespace',
            default_value='',
            description='set namespace for robot nodes'
        ),
        DeclareLaunchArgument(
            'sim_mode',
            default_value='false'
        ),
        LogInfo(msg='\033[96;1;4msim mode active\033[0m', condition=IfCondition(sim_mode)),
        GroupAction(
            actions=[
                PushRosNamespace(robot_namespace),
                slam,
                lidars,
            ]
        )
    ])
