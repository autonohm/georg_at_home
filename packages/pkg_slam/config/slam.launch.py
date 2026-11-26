from launch import LaunchDescription
from launch_ros.actions import Node

from launch.actions import IncludeLaunchDescription
from launch.substitutions import PathJoinSubstitution

from launch_ros.substitutions import FindPackageShare

from launch.substitutions import LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue



def generate_launch_description():
    sim_mode = LaunchConfiguration('sim_mode')

    rf2o_odom = Node(
        package='rf2o_laser_odometry',
        executable='rf2o_laser_odometry_node',
        # no name because rf2o is weird and registers 2 Nodes
        parameters=[
            { PathJoinSubstitution([ '.', 'parameters', 'rf2o_laser_odometry.yaml' ]) },
            { 'use_sim_time': sim_mode },
            # Only one node may publish odom -> base_footprint. On the robot that is the
            # wheel odometry of pkg_drive (odom/wheel); in sim mode there is no drive node,
            # so rf2o publishes the tf there. The odom/lidar topic is published either way.
            { 'publish_tf': ParameterValue(sim_mode, value_type=bool) },
        ],
        arguments=['--ros-args', '--log-level', 'warn'],
        output='screen',
        emulate_tty=True,
    )

    slam_toolbox = IncludeLaunchDescription(
        PathJoinSubstitution([ FindPackageShare('slam_toolbox'), 'launch', 'online_async_launch.py' ]),
        launch_arguments={
            'autostart': 'true',
            'use_lifecycle_manager': 'false',
            'slam_params_file': PathJoinSubstitution([ '.', 'parameters', 'slam_toolbox.yaml' ]),
            'use_sim_time': sim_mode,
        }.items()
    )

    tf_map_odom = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='map_to_odom_tf',
        arguments=[
            "--x", "0.0",
            "--y", "0.0",
            "--z", "0.0",
            "--roll", "0.0",
            "--pitch", "0.0",
            "--yaw", "0.0",
            "--frame-id", "map",  # PathJoinSubstitution([ robot_namespace, 'map' ]),
            "--child-frame-id", "odom",  # PathJoinSubstitution([ robot_namespace, 'odom' ])
        ],
        # remappings=[('/tf','tf'),('/tf_static','tf_static')],
        output="screen",
        emulate_tty=True,
    )

    tf_odom_basefootprint = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='odom_to_base_footprint_tf',
        arguments=[
            "--x", "0.0",
            "--y", "0.0",
            "--z", "0.0",
            "--roll", "0.0",
            "--pitch", "0.0",
            "--yaw", "0.0",
            "--frame-id", 'odom',
            "--child-frame-id", 'base_footprint'
        ],
        # remappings=[('/tf','tf'),('/tf_static','tf_static')],
        output="screen",
        emulate_tty=True,
    )

    return LaunchDescription([
        # No static map -> odom here: slam_toolbox publishes map -> odom itself
        # (transform_publish_period), a second publisher makes the tf jump (Nav2 errors).
        # tf_map_odom,
        # tf_odom_basefootprint,

        rf2o_odom,
        slam_toolbox
    ])
