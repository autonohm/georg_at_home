import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node

from datatypes.action import Listen


class SpeechTaskManagerDemo(Node):
    def __init__(self):
        super().__init__("speech_task_manager_demo")

        self.declare_parameter("action_name", "/audio/listen")
        self.declare_parameter("timeout_sec", 10.0)

        action_name = self.get_parameter("action_name").value
        self.timeout_sec = float(self.get_parameter("timeout_sec").value)

        self.client = ActionClient(self, Listen, action_name)
        self.timer = self.create_timer(1.0, self.start_once)
        self.running = False

        self.get_logger().info("[SpeechDemo] Waiting for listen action server...")

    def start_once(self):
        if self.running:
            return

        if not self.client.wait_for_server(timeout_sec=0.1):
            return

        self.running = True
        self.timer.cancel()

        goal = Listen.Goal()
        goal.mode = Listen.Goal.MODE_SPEECH
        goal.timeout_sec = self.timeout_sec

        self.get_logger().info("[SpeechDemo] Listening for speech...")

        future = self.client.send_goal_async(
            goal,
            feedback_callback=self.feedback_callback,
        )
        future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
        self.get_logger().info(f"[SpeechDemo] state: {feedback_msg.feedback.state}")

    def goal_response_callback(self, future):
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().error("[SpeechDemo] Listen goal rejected")
            rclpy.shutdown()
            return

        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result().result

        if result.detected:
            self.get_logger().info(f"\033[1;92m✓ SPEECH: {result.transcript}\033[0m")
        else:
            self.get_logger().info("\033[1;91m✗ NO SPEECH DETECTED\033[0m")

        rclpy.shutdown()


def main(args=None):
    rclpy.init(args=args)
    node = SpeechTaskManagerDemo()

    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()