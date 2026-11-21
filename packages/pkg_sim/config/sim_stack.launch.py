"""Everything for profile sim in one launch (used on a Mac without Docker: pixi run sim).

simulator + SLAM + real navigation + task manager + mocked speech/gestures + command gate,
plus Georg's model (georg_description, if built: pixi run fetch_description && pixi run build).
In Docker the same parts run as separate containers (compose profile sim, model: pkg_urdf).

    ros2 launch sim_stack.launch.py simulator:=simmj mujoco_viewer:=true   # MuJoCo window
"""
import os

from ament_index_python.packages import get_package_share_directory, PackageNotFoundError
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, GroupAction, LogInfo
from launch.actions import IncludeLaunchDescription, OpaqueFunction, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node, PushRosNamespace

HERE = os.path.dirname(os.path.abspath(__file__))
PACKAGES = os.path.abspath(os.path.join(HERE, '..', '..'))


def _description_launch():
    try:
        return os.path.join(get_package_share_directory('georg_description'), 'launch',
                            'publish_urdf.launch.py')
    except PackageNotFoundError:
        return None


def _simulator_and_model(context, maps):
    simulator = LaunchConfiguration('simulator').perform(context)
    viewer = LaunchConfiguration('mujoco_viewer').perform(context).lower() == 'true'
    if viewer and simulator != 'simmj':
        raise RuntimeError('mujoco_viewer:=true needs simulator:=simmj')
    model = _description_launch()
    actions = []
    if model:
        # robot_state_publisher publishes base_footprint -> base_link -> ... and
        # /robot_description (Lichtblick draws Georg from it). No namespace: its own
        # remapping /tf -> tf would otherwise end up on /georg/tf.
        actions.append(IncludeLaunchDescription(model))
    else:
        actions.append(LogInfo(msg='georg_description not built: no robot model '
                                   '(pixi run fetch_description && pixi run build)'))
    actions.append(GroupAction(actions=[
        PushRosNamespace('georg'),
        Node(package='georg_sim', executable=simulator, name='georg_sim', output='screen',
             # macOS: the MuJoCo window needs the main thread, which mjpython provides
             prefix='mjpython' if viewer else None,
             parameters=[{'map_file': os.path.join(maps, 'Nav_Test.yaml'),
                          'publish_base_link_tf': model is None,
                          'viewer': viewer}]),
    ]))
    return actions


def generate_launch_description():
    maps = os.environ.get('GEORG_MAP_DIR', os.path.join(PACKAGES, 'pkg_slam', 'maps'))
    return LaunchDescription([
        DeclareLaunchArgument('simulator', default_value='sim2d',
                              description='sim2d (stage 1) or simmj (MuJoCo, stage 2)'),
        DeclareLaunchArgument('mujoco_viewer', default_value='false',
                              description='open the MuJoCo window (simulator:=simmj only)'),
        SetEnvironmentVariable('GEORG_MAP_DIR', maps),
        SetEnvironmentVariable('GEORG_DEFAULT_MAP', 'Nav_Test.yaml'),
        SetEnvironmentVariable('GEORG_PROFILE', 'sim'),
        OpaqueFunction(function=_simulator_and_model, args=[maps]),
        GroupAction(actions=[
            PushRosNamespace('georg'),
            Node(package='task_manager', executable='task_manager', name='task_manager',
                 output='screen'),
            Node(package='task_manager', executable='mock_packages', name='mock_packages',
                 arguments=['--scenario', 'sim_mocks'], output='screen'),
            Node(package='command_gate', executable='command_gate', name='command_gate',
                 output='screen'),
        ]),
        IncludeLaunchDescription(os.path.join(PACKAGES, 'pkg_navigation', 'config',
                                              'navigation.launch.py')),
        # Lichtblick: ws://localhost:8765 (min_qos_depth 10: no lost status updates)
        Node(package='foxglove_bridge', executable='foxglove_bridge', name='foxglove_bridge',
             parameters=[{'port': 8765, 'min_qos_depth': 10}], output='screen'),
        # slam_sim.launch.py loads its parameters relative to its folder
        ExecuteProcess(cmd=['ros2', 'launch', 'slam_sim.launch.py'],
                       cwd=os.path.join(PACKAGES, 'pkg_slam', 'config'), output='screen'),
    ])
