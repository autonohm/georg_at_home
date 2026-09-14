from launch import LaunchDescription

from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch.actions import IncludeLaunchDescription
from launch.substitutions import EnvironmentVariable, PathJoinSubstitution

from launch.actions import GroupAction
from launch_ros.actions import PushRosNamespace


def generate_launch_description():
    robot_namespace = LaunchConfiguration('robot_namespace')

    slam = IncludeLaunchDescription(
        'slam.launch.py',
    )

    robot_description = IncludeLaunchDescription(
        'robot-description.launch.py',
        launch_arguments={
            'model': 'description/robot.urdf.xacro',
        }.items()
    )

    lidars = IncludeLaunchDescription(
        'lidars.launch.py',
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'robot_namespace',
            default_value='georg',
            description='set namespace for robot nodes'
        ),
        GroupAction(
            actions=[
                # PushRosNamespace(robot_namespace),  => namespace disabled as of now
                slam,
                robot_description,
                lidars,
            ]
        )
    ])
