"""Exercise the ``Listen`` action server in doorbell-detection mode.

The node waits asynchronously for the server, submits a goal, displays action
feedback/results, and optionally repeats the cycle. It serves as an example of
the client-side lifecycle for the custom ``datatypes/action/Listen`` action.
"""

import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from datatypes.action import Listen


class DoorbellTaskManagerDemo(Node):
    """Action client that requests doorbell detection."""

    def __init__(self) -> None:
        """Read client settings and begin polling for the action server."""
        super().__init__("doorbell_task_manager_demo")

        GREEN = "\033[92m"
        RED = "\033[91m"
        RESET = "\033[0m"

        self.declare_parameter("action_name", "/audio/listen")
        self.declare_parameter("timeout_sec", 30.0)
        self.declare_parameter("repeat", True)

        action_name = self.get_parameter("action_name").value
        self.timeout_sec = float(self.get_parameter("timeout_sec").value)
        self.repeat = bool(self.get_parameter("repeat").value)

        self.client = ActionClient(self, Listen, action_name)
        # A timer keeps startup non-blocking while the server loads its models.
        self.timer = self.create_timer(1.0, self.start_once)
        self.running = False

        self.get_logger().info("[TaskManagerDemo] Waiting for listen action server...")

    def start_once(self) -> None:
        """Submit a doorbell goal once the action server becomes available."""
        if self.running:
            return

        if not self.client.wait_for_server(timeout_sec=0.1):
            return

        self.running = True
        # Stop polling before sending to prevent overlapping action goals.
        self.timer.cancel()

        goal = Listen.Goal()
        goal.mode = Listen.Goal.MODE_DOORBELL
        goal.timeout_sec = self.timeout_sec

        self.get_logger().info("[TaskManagerDemo] Listening for doorbell...")

        future = self.client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback,
        )
        future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg) -> None:
        """Report a state update published by the action server."""
        self.get_logger().info(
            f"[TaskManagerDemo] listen state: {feedback_msg.feedback.state}"
        )

    def goal_response_callback(self, future) -> None:
        """Handle goal acceptance and attach the asynchronous result callback."""
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error("[TaskManagerDemo] Listen goal rejected")
            rclpy.shutdown()
            return

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future) -> None:
        """Display the completed result and either repeat or stop ROS."""
        result = future.result().result

        if result.detected:
            self.get_logger().info(
                f"\033[1;92m"
                f"DOORBELL DETECTED (confidence={result.confidence:.3f})"
                f"\033[0m"
            )
        else:
            self.get_logger().info(
                f"\033[1;91m"
                f"NO DOORBELL DETECTED (confidence={result.confidence:.3f})"
                f"\033[0m"
            )

        if self.repeat:
            self.running = False
            self.timer = self.create_timer(1.0, self.start_once)
        else:
            rclpy.shutdown()


def main(args=None) -> None:
    """Run the action-client demo with graceful keyboard-interrupt cleanup."""
    rclpy.init(args=args)
    node = DoorbellTaskManagerDemo()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
