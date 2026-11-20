"""Everything for profile sim in one launch (used on a Mac without Docker: pixi run sim).

simulator + SLAM + real navigation + task manager + mocked speech/gestures + command gate.
In Docker the same parts run as separate containers (compose profile sim).
"""
import os

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, GroupAction
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGES = os.path.abspath(os.path.join(HERE, '..', '..'))


def generate_launch_description():
    simulator = LaunchConfiguration('simulator')
    maps = os.environ.get('GEORG_MAP_DIR', os.path.join(PACKAGES, 'pkg_slam', 'maps'))
    return LaunchDescription([
        DeclareLaunchArgument('simulator', default_value='sim2d',
                              description='sim2d (stage 1) or simmj (MuJoCo, stage 2)'),
        SetEnvironmentVariable('GEORG_MAP_DIR', maps),
        SetEnvironmentVariable('GEORG_DEFAULT_MAP', 'Nav_Test.yaml'),
        SetEnvironmentVariable('GEORG_PROFILE', 'sim'),
        GroupAction(actions=[
            PushRosNamespace('georg'),
            Node(package='georg_sim', executable=simulator, name='georg_sim', output='screen',
                 parameters=[{'map_file': os.path.join(maps, 'Nav_Test.yaml')}]),
            Node(package='georg_task_manager', executable='task_manager', name='task_manager',
                 output='screen'),
            Node(package='georg_task_manager', executable='mock_packages', name='mock_packages',
                 arguments=['--scenario', 'sim_mocks'], output='screen'),
            Node(package='command_gate', executable='command_gate', name='command_gate',
                 output='screen'),
        ]),
        IncludeLaunchDescription(os.path.join(PACKAGES, 'pkg_navigation', 'config',
                                              'navigation.launch.py')),
        # slam_sim.launch.py loads its parameters relative to its folder
        ExecuteProcess(cmd=['ros2', 'launch', 'slam_sim.launch.py'],
                       cwd=os.path.join(PACKAGES, 'pkg_slam', 'config'), output='screen'),
    ])
