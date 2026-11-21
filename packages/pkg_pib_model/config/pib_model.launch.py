"""pib model on Georg: joint state conversion, mount tf, robot_state_publisher, fake motors.

Profile sim (GEORG_PROFILE): fake pib motors instead of pib-backend (no hardware).
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    model = os.path.join(get_package_share_directory('pib_model'), 'model')
    with open(os.path.join(model, 'pib.urdf'), encoding='utf-8') as f:
        urdf = f.read()
    nodes = [
        Node(package='pib_model', executable='pib_model_node', name='pib_model',
             output='screen'),
        # tf of the pib links from pib/joint_states (URDF joint names)
        Node(package='robot_state_publisher', executable='robot_state_publisher',
             name='robot_state_publisher', namespace='pib',
             parameters=[{'robot_description': urdf}], output='screen'),
    ]
    if os.environ.get('GEORG_PROFILE') == 'sim':
        nodes.append(Node(package='pib_model', executable='fake_pib_motors',
                          name='fake_pib_motors', output='screen'))
    return LaunchDescription(nodes)
