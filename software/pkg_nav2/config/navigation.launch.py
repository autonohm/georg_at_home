# Copyright (C) 2023 Open Source Robotics Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This is all-in-one launch script intended for use by nav2 developers."""

import os
import tempfile

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription,
                            OpaqueFunction, RegisterEventHandler)
from launch.conditions import IfCondition
from launch.event_handlers import OnShutdown
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare
# from nav2_common.launch import LaunchConfigAsBool


def generate_launch_description() -> LaunchDescription:
    # Get the launch directory
    sim_dir = get_package_share_directory('nav2_minimal_tb3_sim')

    # Create the launch configuration variables
    # slam = LaunchConfigAsBool('slam')
    namespace = LaunchConfiguration('namespace')
    map_yaml_file = LaunchConfiguration('map')
    graph_filepath = LaunchConfiguration('graph')
    # use_sim_time = LaunchConfigAsBool('use_sim_time')
    params_file = LaunchConfiguration('params_file')
    autostart = LaunchConfiguration('autostart')
    # use_composition = LaunchConfigAsBool('use_composition')
    # use_intra_process_comms = LaunchConfigAsBool('use_intra_process_comms')
    # use_respawn = LaunchConfigAsBool('use_respawn')

    # Launch configuration variables specific to simulation
    rviz_config_file = LaunchConfiguration('rviz_config_file')
    # use_simulator = LaunchConfigAsBool('use_simulator')
    # use_robot_state_pub = LaunchConfigAsBool('use_robot_state_pub')
    # use_rviz = LaunchConfigAsBool('use_rviz')
    # headless = LaunchConfigAsBool('headless')
    world = LaunchConfiguration('world')
    pose = {
        'x': LaunchConfiguration('x_pose', default='-2.00'),
        'y': LaunchConfiguration('y_pose', default='-0.50'),
        'z': LaunchConfiguration('z_pose', default='0.01'),
        'R': LaunchConfiguration('roll', default='0.00'),
        'P': LaunchConfiguration('pitch', default='0.00'),
        'Y': LaunchConfiguration('yaw', default='0.00'),
    }
    robot_name = LaunchConfiguration('robot_name')
    robot_sdf = LaunchConfiguration('robot_sdf')

    remappings = [('/tf', 'tf'), ('/tf_static', 'tf_static')]

    # Declare the launch arguments
    declare_namespace_cmd = DeclareLaunchArgument(
        'namespace', default_value='', description='Top-level namespace'
    )

    declare_slam_cmd = DeclareLaunchArgument(
        'slam', default_value='False', description='Whether run a SLAM'
    )

    # declare_map_yaml_cmd = DeclareLaunchArgument(
    #     'map',
    #     default_value=os.path.join(bringup_dir, 'maps', 'tb3_sandbox.yaml'),
    # )
    #
    # declare_graph_file_cmd = DeclareLaunchArgument(
    #     'graph',
    #     default_value=os.path.join(bringup_dir, 'graphs', 'turtlebot3_graph.geojson'),
    # )

    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true',
    )

    # declare_params_file_cmd = DeclareLaunchArgument(
    #     'params_file',
    #     default_value=os.path.join(bringup_dir, 'params', 'nav2_params.yaml'),
    #     description='Full path to the ROS2 parameters file to use for all launched nodes',
    # )

    declare_autostart_cmd = DeclareLaunchArgument(
        'autostart',
        default_value='true',
        description='Automatically startup the nav2 stack',
    )

    declare_use_composition_cmd = DeclareLaunchArgument(
        'use_composition',
        default_value='True',
        description='Whether to use composed bringup',
    )

    declare_use_intra_process_comms_cmd = DeclareLaunchArgument(
        'use_intra_process_comms',
        default_value='False',
        description='Whether to use intra process communication',
    )

    declare_use_respawn_cmd = DeclareLaunchArgument(
        'use_respawn',
        default_value='False',
        description='Whether to respawn if a node crashes. Applied when composition is disabled.',
    )


    # bringup_cmd = IncludeLaunchDescription(
    #     PythonLaunchDescriptionSource(PathJoinSubstitution([FindPackageShare('nav2_bringup'), 'launch', 'bringup_launch.py'])),
    #     launch_arguments={
    #         'namespace': namespace,
    #         'slam': slam,
    #         'use_localization': 'True',
    #         'serve_static_map': 'True',
    #         'map': map_yaml_file,
    #         'graph': graph_filepath,
    #         'use_sim_time': use_sim_time,
    #         'params_file': params_file,
    #         'autostart': autostart,
    #         'use_composition': use_composition,
    #         'use_intra_process_comms': use_intra_process_comms,
    #         'use_respawn': use_respawn,
    #         'use_keepout_zones': 'False',
    #         'use_speed_zones': 'False',
    #         'container_name': 'nav2_container',
    #     }.items(),
    # )

    bringup_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(PathJoinSubstitution([FindPackageShare('nav2_bringup'), 'launch', 'bringup_launch.py'])),
        launch_arguments={
            'namespace': 'georg',
            #'slam': False,
            #'use_localization': 'True',
            #'serve_static_map': 'True',
            #'map': map_yaml_file,
            # 'graph': graph_filepath,
            #'use_sim_time': False,
            'params_file': "/config/parameters/nav2_params.yaml",
            #'autostart': True,
            #'use_composition': True,
            #'use_intra_process_comms': True,
            #'use_respawn': use_respawn,
            #'use_keepout_zones': 'False',
            #'use_speed_zones': 'False',
            #'container_name': 'nav2_container',
        }.items(),
    )

    # Create the launch description and populate
    ld = LaunchDescription()

    # Declare the launch options
    ld.add_action(declare_namespace_cmd)
    ld.add_action(declare_slam_cmd)
    # ld.add_action(declare_map_yaml_cmd)
    # ld.add_action(declare_graph_file_cmd)
    ld.add_action(declare_use_sim_time_cmd)
    # ld.add_action(declare_params_file_cmd)
    ld.add_action(declare_autostart_cmd)
    ld.add_action(declare_use_composition_cmd)
    ld.add_action(declare_use_intra_process_comms_cmd)


    ld.add_action(declare_use_respawn_cmd)


    # Add the actions to launch all of the navigation nodes
    ld.add_action(bringup_cmd)

    return ld