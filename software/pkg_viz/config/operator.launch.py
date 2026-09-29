import os

from launch import LaunchDescription
from launch_ros.actions import Node


from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch.actions import GroupAction
from launch_ros.actions import PushRosNamespace

from launch.substitutions import PathJoinSubstitution


def generate_launch_description():

    robot_namespace = LaunchConfiguration('robot_namespace')

    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz',
        arguments=['-d', PathJoinSubstitution([ os.getcwd(), 'config/georg.rviz' ])],
        emulate_tty=True,
    )

    rqt = Node(
        package='rqt_gui',
        executable='rqt_gui',
        name='rqt',
        arguments=['--perspective-file', PathJoinSubstitution([ os.getcwd(), 'config/rviz.perspective'])],
        output='log',
        emulate_tty=True,
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'robot_namespace',
            default_value='georg',
            description='set namespace for robot nodes'
        ),
        GroupAction(
        actions=[
            # PushRosNamespace( [LaunchConfiguration("robot_namespace"), '_opr'] ),
            rviz,
            # rqt,
        ]),
    ])
