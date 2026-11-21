"""Fake pib motors for mock/sim: behaves like motor_control of pib-backend, no hardware.

    /joint_states      (sensor_msgs/JointState) motor names, positions in centidegrees, 10 Hz
    /joint_trajectory  (trajectory_msgs/JointTrajectory) feedback per moved motor, radians
    /apply_joint_trajectory (datatypes/srv/ApplyJointTrajectory, radians) - only if the
                        pib-backend message package `datatypes` is installed (plan phase 5)
    fake_motors/command (trajectory_msgs/JointTrajectory, motor names, radians) - same as the
                        service, for tests and as long as the service is missing

Every motor moves towards its target with max_speed_deg_s (no physics).
"""
import json
import math
import os

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint

from pib_model.mapping import MotorMapping

try:
    from datatypes.srv import ApplyJointTrajectory
except ImportError:  # pib-backend datatypes not in the image yet
    ApplyJointTrajectory = None


class FakeMotors(Node):
    """Motor positions in centidegrees that follow commanded targets."""

    def __init__(self):
        """Read the motor names from mapping.json and set up the interfaces."""
        super().__init__('fake_pib_motors')
        model_dir = self.declare_parameter('model_dir', '').value
        if not model_dir:
            from ament_index_python.packages import get_package_share_directory
            model_dir = os.path.join(get_package_share_directory('pib_model'), 'model')
        self.speed = self.declare_parameter('max_speed_deg_s', 90.0).value * 100.0
        with open(os.path.join(model_dir, 'mapping.json'), encoding='utf-8') as f:
            names = MotorMapping(json.load(f)).motor_names
        self.position = {n: 0.0 for n in names}
        self.target = dict(self.position)
        self.state_pub = self.create_publisher(JointState, 'joint_states', 10)
        self.feedback_pub = self.create_publisher(JointTrajectory, 'joint_trajectory', 10)
        self.create_subscription(JointTrajectory, 'fake_motors/command', self._on_command, 10)
        if ApplyJointTrajectory is not None:
            self.create_service(ApplyJointTrajectory, 'apply_joint_trajectory', self._on_apply)
        self.dt = 0.1
        self.create_timer(self.dt, self._step)
        self.get_logger().info(
            f'fake pib motors: {len(names)} motors, service apply_joint_trajectory '
            f'{"on" if ApplyJointTrajectory else "off (datatypes of pib-backend missing)"}')

    def _set_targets(self, trajectory):
        """Take the last point of the trajectory as target; returns False on unknown names."""
        if not trajectory.points:
            return False
        point = trajectory.points[-1]
        unknown = [n for n in trajectory.joint_names if n not in self.target]
        if unknown:
            self.get_logger().warn(f'unknown motors ignored: {unknown}')
        for name, rad in zip(trajectory.joint_names, point.positions):
            if name in self.target:
                self.target[name] = math.degrees(rad) * 100.0
        return not unknown

    def _on_command(self, msg):
        self._set_targets(msg)

    def _on_apply(self, request, response):
        ok = self._set_targets(request.joint_trajectory)
        if hasattr(response, 'successful'):
            response.successful = ok
        return response

    def _step(self):
        max_step = self.speed * self.dt
        for name, target in self.target.items():
            diff = target - self.position[name]
            if abs(diff) > 1e-6:
                self.position[name] += max(-max_step, min(max_step, diff))
                self._feedback(name)
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(self.position)
        msg.position = [self.position[n] for n in msg.name]
        self.state_pub.publish(msg)

    def _feedback(self, name):
        jt = JointTrajectory()
        jt.header.stamp = self.get_clock().now().to_msg()
        jt.joint_names = [name]
        point = JointTrajectoryPoint()
        point.positions = [math.radians(self.position[name] / 100.0)]
        jt.points = [point]
        self.feedback_pub.publish(jt)


def main():
    """Run the node."""
    rclpy.init()
    node = FakeMotors()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
