from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', LaunchConfiguration('model')])}]
    )

    return LaunchDescription([
        DeclareLaunchArgument(name='model', default_value="description/georg_base.urdf.xacro", description='Absolute path to robot model file'),
        robot_state_publisher_node,
    ])
