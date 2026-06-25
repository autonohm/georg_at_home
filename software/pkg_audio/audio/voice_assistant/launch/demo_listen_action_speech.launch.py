from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    wav_path = LaunchConfiguration("wav_path")
    timeout_sec = LaunchConfiguration("timeout_sec")
    speech_model_size = LaunchConfiguration("speech_model_size")
    speech_language = LaunchConfiguration("speech_language")

    return LaunchDescription([
        DeclareLaunchArgument("wav_path", default_value=""),
        DeclareLaunchArgument("timeout_sec", default_value="10.0"),
        DeclareLaunchArgument("speech_model_size", default_value="base"),
        DeclareLaunchArgument("speech_language", default_value="de"),

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
            }],
        ),

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