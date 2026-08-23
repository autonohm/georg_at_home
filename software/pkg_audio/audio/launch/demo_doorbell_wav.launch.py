"""Launch the YAMNet doorbell-detection pipeline for a WAV file.

The detector analyses the configured file once, publishes a ``VoiceEvent`` for
a qualifying doorbell sound, and lets the rule engine and dispatcher exercise
the remainder of the event-to-task pipeline.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    """Build the one-shot WAV detection demo."""
    # Values remain substitutions until ROS evaluates the launch description.
    wav_path = LaunchConfiguration("wav_path")
    doorbell_threshold = LaunchConfiguration("doorbell_threshold")
    speech_max_threshold = LaunchConfiguration("speech_max_threshold")

    return LaunchDescription([
        # An empty path is accepted by launch but reported by the detector.
        DeclareLaunchArgument("wav_path", default_value=""),
        DeclareLaunchArgument("doorbell_threshold", default_value="0.30"),
        DeclareLaunchArgument("speech_max_threshold", default_value="0.25"),

        # Consume the VoiceTask emitted by the rule engine.
        Node(
            package="voice_assistant",
            executable="voice_task_dispatcher",
            name="voice_task_dispatcher",
            output="screen",
        ),

        # Convert recognized voice events into task-management commands.
        Node(
            package="voice_assistant",
            executable="voice_rule_engine",
            name="voice_rule_engine",
            output="screen",
        ),

        # Run ML inference on the WAV file once after node startup.
        Node(
            package="voice_assistant",
            executable="doorbell_wav_detector",
            name="doorbell_wav_detector",
            output="screen",
            parameters=[{
                "wav_path": wav_path,
                "doorbell_threshold": doorbell_threshold,
                "speech_max_threshold": speech_max_threshold,
            }],
        ),
    ])
