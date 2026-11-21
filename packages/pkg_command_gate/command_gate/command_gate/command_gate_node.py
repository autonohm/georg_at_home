"""command_gate: forwards motor commands to the driver only in mode 'real'.

    cmd_vel (Twist) --> [command_gate] --> cmd_vel/gated (Twist) --> driver

Outside 'real' every message is dropped and logged (throttled). The mode is
re-checked every second, so removing the mode file closes the gate at once.
"""

import os

from command_gate.gate import device_mode, is_open
from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node


class CommandGate(Node):

    def __init__(self):
        super().__init__('command_gate')
        self._profile = os.environ.get('GEORG_PROFILE', '')
        self._open = False
        self._announced = False
        self._dropped = 0
        self._pub = self.create_publisher(Twist, 'cmd_vel/gated', 10)
        self.create_subscription(Twist, 'cmd_vel', self._on_cmd_vel, 10)
        self._refresh()
        self.create_timer(1.0, self._refresh)

    def _refresh(self):
        device = device_mode()
        now_open = is_open(device, self._profile)
        if now_open != self._open or not self._announced:
            self._announced = True
            state = 'OPEN (forwarding)' if now_open else 'CLOSED (dropping)'
            self.get_logger().info(
                f"gate {state}: device_mode='{device}' profile='{self._profile}'")
        self._open = now_open

    def _on_cmd_vel(self, msg: Twist):
        if self._open:
            self._pub.publish(msg)
            return
        self._dropped += 1
        self.get_logger().warn(
            f"dropped motor command #{self._dropped} (mode is not 'real')",
            throttle_duration_sec=5.0)


def main(args=None):
    rclpy.init(args=args)
    node = CommandGate()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
