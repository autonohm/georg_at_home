import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node


def generate_launch_description():
    # robot namespace
    edu_robot_namespace = LaunchConfiguration('edu_robot_namespace')
    edu_robot_namespace_arg = DeclareLaunchArgument(
        'edu_robot_namespace', default_value=os.getenv('EDU_ROBOT_NAMESPACE', default='georg')
    )

    # nodes
    timed_publisher = Node(
      package='pib_topic_template',
      executable='timed_publisher',
      namespace=edu_robot_namespace
    )

    subscriber = Node(
      package='pib_topic_template',
      executable='subscriber',
      namespace=edu_robot_namespace
    )

    action_server = Node(
      package='pib_action_template',
      executable='action_demo_server.py',
      namespace=edu_robot_namespace
    )

    action_client = Node(
      package='pib_action_template',
      executable='action_demo_client.py',
      namespace=edu_robot_namespace
    )

    return LaunchDescription([
      edu_robot_namespace_arg,
      timed_publisher,
      subscriber,
      action_server,
      action_client
    ])
