"""Launch an action server and client demo for speech transcription.

The launch arguments expose speech detection, capture-window, and Whisper
settings. A WAV path provides reproducible input; an empty path selects the
system microphone.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description() -> LaunchDescription:
    """Build the speech-mode ``Listen`` action demonstration."""
    wav_path = LaunchConfiguration("wav_path")
    timeout_sec = LaunchConfiguration("timeout_sec")
    speech_model_size = LaunchConfiguration("speech_model_size")
    speech_language = LaunchConfiguration("speech_language")
    speech_threshold = LaunchConfiguration("speech_threshold")
    speech_pre_roll_sec = LaunchConfiguration("speech_pre_roll_sec")
    speech_tail_sec = LaunchConfiguration("speech_tail_sec")
    speech_max_segment_sec = LaunchConfiguration("speech_max_segment_sec")

    return LaunchDescription([
        DeclareLaunchArgument("wav_path", default_value=""),
        DeclareLaunchArgument("timeout_sec", default_value="10.0"),
        DeclareLaunchArgument("speech_model_size", default_value="tiny"),
        DeclareLaunchArgument("speech_language", default_value="de"),
        DeclareLaunchArgument("speech_threshold", default_value="0.30"),
        DeclareLaunchArgument("speech_pre_roll_sec", default_value="0.5"),
        DeclareLaunchArgument("speech_tail_sec", default_value="1.2"),
        DeclareLaunchArgument("speech_max_segment_sec", default_value="5.0"),

        # Detect a speech segment and transcribe it for each accepted goal.
        Node(
            package="voice_assistant",
            executable="listen_action_server",
            name="voice_listen_action_server",
            output="screen",
            parameters=[{
                "wav_path": wav_path,
                "timeout_sec": timeout_sec,
                "speech_model_size": speech_model_size,
                "speech_language": speech_language,
                "speech_threshold": speech_threshold,
                "speech_pre_roll_sec": speech_pre_roll_sec,
                "speech_tail_sec": speech_tail_sec,
                "speech_max_segment_sec": speech_max_segment_sec,
            }],
        ),

        # Submit one MODE_SPEECH goal and display feedback and the transcript.
        Node(
            package="voice_assistant",
            executable="speech_task_manager_demo",
            name="speech_task_manager_demo",
            output="screen",
            parameters=[{
                "timeout_sec": timeout_sec,
            }],
        ),
    ])
