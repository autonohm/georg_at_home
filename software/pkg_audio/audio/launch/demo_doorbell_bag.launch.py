"""Launch the threshold-based doorbell demo with a recorded ROS bag.

The launch graph replays an ``Int16MultiArray`` audio topic from a bag, converts
high-amplitude chunks into ``VoiceEvent`` messages, maps those events to
``VoiceTask`` messages, and finally passes the tasks to the demo dispatcher.

Launch arguments:
    bag_path: Path to the rosbag that supplies the audio stream.
    audio_topic: Topic in the bag containing signed 16-bit PCM samples.
    threshold: Minimum RMS amplitude that is treated as a doorbell candidate.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    """Build the nodes and bag playback process for the streaming demo."""
    # LaunchConfiguration objects are resolved by ROS at launch time, allowing
    # callers to override the defaults from the command line.
    bag_path = LaunchConfiguration("bag_path")
    audio_topic = LaunchConfiguration("audio_topic")
    threshold = LaunchConfiguration("threshold")

    return LaunchDescription([
        # Declare every externally configurable value before it is consumed.
        DeclareLaunchArgument("bag_path", default_value=""),
        DeclareLaunchArgument("audio_topic", default_value="/audio_stream"),
        DeclareLaunchArgument("threshold", default_value="1000"),

        # The dispatcher is the final demo sink for generated VoiceTask messages.
        Node(
            package="voice_assistant",
            executable="voice_task_dispatcher",
            name="voice_task_dispatcher",
            output="screen",
        ),

        # The rule engine translates detector events into actionable tasks.
        Node(
            package="voice_assistant",
            executable="voice_rule_engine",
            name="voice_rule_engine",
            output="screen",
        ),

        # This lightweight detector uses RMS amplitude rather than YAMNet.
        Node(
            package="voice_assistant",
            executable="doorbell_audio_stream_detector",
            name="doorbell_audio_stream_detector",
            output="screen",
            parameters=[{
                "audio_topic": audio_topic,
                "threshold": threshold,
            }],
        ),

        # Start bag playback alongside the ROS nodes so recorded audio is
        # delivered through exactly the same topic interface as live audio.
        ExecuteProcess(
            cmd=["ros2", "bag", "play", bag_path],
            output="screen",
        ),
    ])
