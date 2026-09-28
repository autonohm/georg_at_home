import os
import pathlib

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare

from launch.actions import GroupAction
from launch_ros.actions import PushRosNamespace, Node


def generate_launch_description():
    # robot namespace
    robot_namespace = LaunchConfiguration('robot_namespace')
    robot_namespace_arg = DeclareLaunchArgument(
        'robot_namespace', default_value=os.getenv('EDU_ROBOT_NAMESPACE', default='georg')
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
      emulate_tty=True,
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
      remappings=[('twist_limiter/in', 'limiter/cmd_vel'),
                  ('twist_limiter/out', 'cmd_vel')],
      emulate_tty=True,
    )

    remote_control_node = Node(
      package='edu_robot_control',
      executable='remote_control',
      parameters=[PathJoinSubstitution([cwd_path, 'edu_robot_control.yaml'])],
      remappings=[('cmd_vel', 'teleop/cmd_vel')],
      emulate_tty=True,
    )

    joy_node = Node(
      package='joy_linux',
      executable='joy_linux_node',
      parameters=[
        {'autorepeat_rate': 20.0},
        {'coalesce_interval_ms': 50},
        {'dev': '/dev/georg_controller'}
      ],
      emulate_tty=True,
    )

    twist_mux = IncludeLaunchDescription(
        PathJoinSubstitution([FindPackageShare('twist_mux'), 'launch', 'twist_mux_launch.py']),
        launch_arguments={
            'config_locks': '/config/twist_mux/twist_mux_locks.yaml',
            'config_topics': '/config/twist_mux/twist_mux_topics.yaml',
            'config_joy': '/config/twist_mux/joystick.yaml',
            'cmd_vel_out': 'limiter/cmd_vel',
            'use_sim_time': 'False',
        }.items()
    )


    return LaunchDescription([
        robot_namespace_arg,
        GroupAction(
            actions=[
                PushRosNamespace(robot_namespace),
                twist_limiter,
                remote_control_node,
                joy_node,
                twist_mux,
                drive_node,
            ]
        ),
    ])
