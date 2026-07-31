"""Exercise the ``Listen`` action server in speech-transcription mode."""

import rclpy
from datatypes.action import Listen
from rclpy.action import ActionClient
from rclpy.node import Node


class TerminalColor:
    """ANSI escape sequences used to make terminal feedback scannable."""
    RESET = "\033[0m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"


FEEDBACK_MESSAGES = {
    "listening": ("Listening for doorbell...", TerminalColor.BLUE),
    "listening_for_speech": ("Preparing microphone for speech...", TerminalColor.BLUE),
    "ready_for_speech": ("Microphone ready. You can speak now.", TerminalColor.GREEN),
    "speech_detected": ("Speech detected. Keep speaking...", TerminalColor.YELLOW),
    "transcribing": ("Transcribing speech...", TerminalColor.CYAN),
    "speech_transcribed": ("Speech transcribed.", TerminalColor.GREEN),
    "no_speech_detected": ("No speech detected.", TerminalColor.RED),
    "no_transcript": ("Speech detected, but no transcript was created.", TerminalColor.RED),
    "doorbell_detected": ("Doorbell detected.", TerminalColor.GREEN),
    "timeout": ("Timeout. Nothing detected.", TerminalColor.RED),
    "cancelled": ("Listen goal cancelled.", TerminalColor.RED),
    "error": ("An error occurred.", TerminalColor.RED),
}


class SpeechTaskManagerDemo(Node):
    """Submit one speech goal and print its feedback and transcript."""

    def __init__(self) -> None:
        """Read parameters and begin asynchronously waiting for the server."""
        super().__init__("speech_task_manager_demo")

        self.declare_parameter("action_name", "/audio/listen")
        self.declare_parameter("timeout_sec", 10.0)

        action_name = self.get_parameter("action_name").value
        self.timeout_sec = float(self.get_parameter("timeout_sec").value)

        self.client = ActionClient(self, Listen, action_name)

        self.goal_sent = False
        self.timer = self.create_timer(1.0, self._try_send_goal)

        self.get_logger().info("[SpeechDemo] Waiting for listen action server...")

    def _try_send_goal(self) -> None:
        """Send a speech goal once, after the action endpoint is available."""
        if self.goal_sent:
            return

        if not self.client.wait_for_server(timeout_sec=0.1):
            return

        self.goal_sent = True
        self.timer.cancel()

        goal = Listen.Goal()
        goal.mode = Listen.Goal.MODE_SPEECH
        goal.timeout_sec = self.timeout_sec

        self.get_logger().info(
            f"{TerminalColor.BLUE}[SpeechDemo] Starting speech listen goal..."
            f"{TerminalColor.RESET}"
        )

        send_goal_future = self.client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback,
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future) -> None:
        """React to goal acceptance and request its eventual result."""
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error(
                f"{TerminalColor.RED}[SpeechDemo] Goal rejected."
                f"{TerminalColor.RESET}"
            )
            rclpy.shutdown()
            return

        self.get_logger().info(
            f"{TerminalColor.GREEN}[SpeechDemo] Goal accepted."
            f"{TerminalColor.RESET}"
        )

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def feedback_callback(self, feedback_msg) -> None:
        """Translate machine-readable action state into a colored message."""
        state = feedback_msg.feedback.state

        message, color = FEEDBACK_MESSAGES.get(
            state,
            (f"State: {state}", TerminalColor.RESET),
        )

        self.get_logger().info(
            f"{color}[SpeechDemo] {message}{TerminalColor.RESET}"
        )

    def result_callback(self, future) -> None:
        """Display the final transcript and end the one-shot demo."""
        result = future.result().result

        if result.detected:
            self.get_logger().info(
                f"{TerminalColor.GREEN}"
                f"[SpeechDemo] ✓ SPEECH: {result.transcript} "
                f"(confidence={result.confidence:.3f})"
                f"{TerminalColor.RESET}"
            )
        else:
            self.get_logger().info(
                f"{TerminalColor.RED}"
                f"[SpeechDemo] ✗ No speech detected "
                f"(confidence={result.confidence:.3f})"
                f"{TerminalColor.RESET}"
            )

        rclpy.shutdown()


def main(args=None) -> None:
    """Run the speech client with reliable cleanup on interruption."""
    rclpy.init(args=args)
    node = SpeechTaskManagerDemo()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
