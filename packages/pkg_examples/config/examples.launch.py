import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def generate_launch_description():
    # robot namespace
    robot_namespace = LaunchConfiguration('robot_namespace')
    robot_namespace_arg = DeclareLaunchArgument(
        'robot_namespace', default_value=os.getenv('EDU_ROBOT_NAMESPACE', default='')
    )

    # nodes
    timed_publisher = Node(
      package='pib_topic_template',
      executable='timed_publisher',
      namespace=robot_namespace
    )

    subscriber = Node(
      package='pib_topic_template',
      executable='subscriber',
      namespace=robot_namespace
    )

    action_server = Node(
      package='pib_action_template',
      executable='action_demo_server.py',
      namespace=robot_namespace
    )

    action_client = Node(
      package='pib_action_template',
      executable='action_demo_client.py',
      namespace=robot_namespace
    )

    return LaunchDescription([
      robot_namespace_arg,
      timed_publisher,
      subscriber,
      action_server,
      action_client
    ])
