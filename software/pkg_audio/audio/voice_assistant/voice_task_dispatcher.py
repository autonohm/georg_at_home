"""Demonstration sink for voice tasks produced by the rule engine.

The current implementation logs the hand-off boundary. A production
integration can replace the log statements with calls into task management
without changing the upstream event and rule-engine nodes.
"""

import json
import rclpy
from rclpy.node import Node
from datatypes.msg import VoiceTask


class VoiceTaskDispatcher(Node):
    """Subscribe to and report generated ``VoiceTask`` messages."""

    def __init__(self) -> None:
        """Connect the dispatcher to the shared task topic."""
        super().__init__("voice_task_dispatcher")

        self.subscription = self.create_subscription(
            VoiceTask,
            "/voice/tasks",
            self.handle_task,
            10,
        )

        self.get_logger().info("[Dispatcher] Ready. Waiting for voice tasks.")

    def handle_task(self, task: VoiceTask) -> None:
        """Log the task fields that would be submitted downstream."""
        self.get_logger().info(
            f"[Dispatcher] Submitted task to taskmanagement: {task.task_type}"
        )
        self.get_logger().info(
            f"[Dispatcher] priority={task.priority}, source_event={task.source_event_type}, metadata={task.metadata_json}"
        )


def main(args=None) -> None:
    """Run the dispatcher until ROS shuts down."""
    rclpy.init(args=args)
    node = VoiceTaskDispatcher()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
