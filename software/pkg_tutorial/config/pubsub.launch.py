from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='py_pubsub',
            executable='talker',
            name='pub',
            emulate_tty=True,
        ),
        Node(
            package='py_pubsub',
            executable='listener',
            name='sub',
            emulate_tty=True,
        )
    ])
