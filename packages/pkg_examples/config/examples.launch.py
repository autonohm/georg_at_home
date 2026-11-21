import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

from launch_ros.actions import Node, PushRosNamespace
from launch.actions import GroupAction
from launch.conditions import IfCondition, UnlessCondition
from launch.actions import LogInfo

def generate_launch_description():
    # robot namespace
    robot_namespace = LaunchConfiguration('robot_namespace')
    robot_namespace_arg = DeclareLaunchArgument(
        'robot_namespace', default_value=os.getenv('EDU_ROBOT_NAMESPACE', default='')
    )
    sim_mode = LaunchConfiguration('sim_mode')
    sim_mode_arg = DeclareLaunchArgument(
        'sim_mode', default_value='false'
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
      sim_mode_arg,
        LogInfo(msg='\033[96;1;4mRunning on real hardware, not starting nodes\033[0m', condition=UnlessCondition(sim_mode)),
        LogInfo(msg='\033[96;1;4msim mode active\033[0m', condition=IfCondition(sim_mode)),
        GroupAction(
          actions=[
            PushRosNamespace(robot_namespace),
            timed_publisher,
            subscriber,
            action_server,
            action_client
          ],
          condition=IfCondition(sim_mode)
        )
    ])
