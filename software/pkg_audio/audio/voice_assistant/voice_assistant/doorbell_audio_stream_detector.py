"""Detect loud audio chunks from a ROS PCM stream.

This intentionally simple detector is useful for integration tests where a
neural classifier would add unnecessary setup cost. Incoming array entries are
interpreted as signed 16-bit samples and compared by RMS amplitude.
"""

import audioop
import json

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int16MultiArray
from datatypes.msg import VoiceEvent


class DoorbellAudioStreamDetector(Node):
    """Convert loud PCM chunks into structured ``VoiceEvent`` messages."""

    def __init__(self) -> None:
        """Load ROS parameters and connect the audio subscription."""
        super().__init__("doorbell_audio_stream_detector")

        self.declare_parameter("audio_topic", "/audio_stream")
        self.declare_parameter("threshold", 1000)
        self.declare_parameter("cooldown_chunks", 20)

        self.audio_topic = self.get_parameter("audio_topic").value
        self.threshold = int(self.get_parameter("threshold").value)
        self.cooldown_chunks = int(self.get_parameter("cooldown_chunks").value)
        # Count processed chunks, not wall-clock time, to suppress duplicate
        # events caused by one loud sound spanning several adjacent messages.
        self.cooldown_left = 0

        self.publisher = self.create_publisher(VoiceEvent, "/voice/events", 10)
        self.subscription = self.create_subscription(
            Int16MultiArray,
            self.audio_topic,
            self.handle_audio_chunk,
            10,
        )

        self.get_logger().info(
            f"[AudioStreamDetector] Ready. Listening on {self.audio_topic}"
        )

    def handle_audio_chunk(self, msg: Int16MultiArray) -> None:
        """Measure one audio chunk and publish when it crosses the threshold."""
        if not msg.data:
            return

        samples = msg.data
        # audioop consumes packed PCM bytes rather than an integer sequence.
        pcm_bytes = b"".join(int(s).to_bytes(2, "little", signed=True) for s in samples)
        rms = audioop.rms(pcm_bytes, 2)

        if self.cooldown_left > 0:
            self.cooldown_left -= 1
            return

        if rms >= self.threshold:
            event = VoiceEvent()
            event.event_type = "doorbell_detected"
            event.confidence = 0.90
            event.source = "audio_stream_threshold_detector"
            event.metadata_json = json.dumps({
                "rms": rms,
                "threshold": self.threshold,
                "audio_topic": self.audio_topic,
            })

            self.publisher.publish(event)
            self.cooldown_left = self.cooldown_chunks

            self.get_logger().info(
                f"[AudioStreamDetector] Published VoiceEvent: {event.event_type}, rms={rms}"
            )


def main(args=None) -> None:
    """Run the detector until ROS requests shutdown."""
    rclpy.init(args=args)
    node = DoorbellAudioStreamDetector()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
