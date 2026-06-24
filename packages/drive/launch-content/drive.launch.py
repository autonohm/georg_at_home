import os
import pathlib

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node


def generate_launch_description():
    # robot namespace
    edu_robot_namespace = LaunchConfiguration('edu_robot_namespace')
    edu_robot_namespace_arg = DeclareLaunchArgument(
        'edu_robot_namespace', default_value=os.getenv('EDU_ROBOT_NAMESPACE', default='georg')
    )
    cwd_path = pathlib.Path(__file__).parent.resolve()

    # nodes

    drive_node = Node(
      package='edu_robot',
      executable='thn-georg-bot',
      name='thn_georg_bot',
      parameters=[PathJoinSubstitution([cwd_path, 'edu_robot.yaml'])],
      namespace='georg',
      # prefix=['gdbserver localhost:3000'],
      output='screen',
      # arguments=[
      #   "--ros-args",
      #   "--log-level",
      #   "edu_robot:=debug"
      # ]
    )

    twist_limiter = Node(
      package='twist_limiter',
      executable='twist_limiter_node',
      parameters=[PathJoinSubstitution([cwd_path, 'twist_limiter.yaml'])],
      remappings=[('twist_limiter/in', 'teleop/cmd_vel'),
                  ('twist_limiter/out', 'cmd_vel')],
      namespace=edu_robot_namespace
    )

    remote_control_node = Node(
      package='edu_robot_control',
      executable='remote_control',
      parameters=[PathJoinSubstitution([cwd_path, 'edu_robot_control.yaml'])],
      remappings=[('cmd_vel', 'teleop/cmd_vel')],
      namespace=edu_robot_namespace
    )

    joy_node = Node(
      package='joy_linux',
      executable='joy_linux_node',
      parameters=[
        {'autorepeat_rate': 20.0},
        {'coalesce_interval_ms': 50},
        {'dev': '/dev/input/js0'}
      ],
      namespace=edu_robot_namespace
    )

    return LaunchDescription([
      edu_robot_namespace_arg,
      twist_limiter,
      remote_control_node,
      joy_node,
      drive_node
    ])
