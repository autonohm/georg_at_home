from launch import LaunchDescription
from launch_ros.actions import Node

from launch_ros.actions import ComposableNodeContainer
from launch_ros.descriptions import ComposableNode

from launch.substitutions import EnvironmentVariable, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    # robot_model = IncludeLaunchDescription(
    #     PathJoinSubstitution([ '.', 'xacro-robot-description.launch.py' ]),
    #     launch_arguments={
    #         'model': PathJoinSubstitution([ '.', 'parameters', 'bento-box-neo.urdf' ]),
    #     }.items()
    # )
    sick_scan_pkg_prefix = FindPackageShare('sick_scan_xd')
    launch_file_path = PathJoinSubstitution([sick_scan_pkg_prefix, 'launch', 'sick_tim_5xx.launch'])  # 'launch/sick_tim_5xx.launch')
    node_arguments=[launch_file_path]


    lidar1 = Node(
            package='sick_scan_xd',
            executable='sick_generic_caller',
            output='screen',
            arguments=[node_arguments, "hostname:=192.168.2.104", "frame_id:=laser1_frame", "tf_publish_rate:=0.0"],
            namespace="lidar1"
    )

    lidar2 = Node(
            package='sick_scan_xd',
            executable='sick_generic_caller',
            output='screen',
            arguments=[node_arguments, "hostname:=192.168.2.144", "frame_id:=laser2_frame", "tf_publish_rate:=0.0"],
            namespace="lidar2"
    )

    scan_merger = ComposableNodeContainer(
        package="rclcpp_components",
        executable="component_container",
        name="component_manager_node",
        namespace="",
        composable_node_descriptions=[
            ComposableNode(
                package="laser_scan_merger",
                plugin="util::LaserScanMerger",
                name="laser_scan_merger_node",
                parameters=[PathJoinSubstitution([ 'parameters', 'scan_merger.yaml' ])]
            )
        ],
        output="screen"
    )

    return LaunchDescription([
        lidar1,
        lidar2,
        scan_merger,
    ])
