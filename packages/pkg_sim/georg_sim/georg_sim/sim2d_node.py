"""2D simulator of Georg (P3, stage 1): same topics as the robot, no physics engine.

Subscribes:  cmd_vel (geometry_msgs/Twist, mecanum: linear.x, linear.y, angular.z)
Publishes:   odom (nav_msgs/Odometry, frame odom -> base_footprint)
             merged_scan and scan (sensor_msgs/LaserScan, frame base_link, 360 deg)
             tf odom -> base_footprint, tf_static base_footprint -> base_link
             (off with publish_base_link_tf:=false when georg_description publishes it)

The odom frame is aligned with the map frame of the map YAML, so odom positions are
map positions (the task manager uses them as start point for navigation). Commands
older than ``cmd_timeout_s`` stop the robot, like a real motor controller. The robot
does not drive through walls: a step that would collide is not executed.

    ros2 run georg_sim sim2d --ros-args -p map_file:=.../Nav_Test.yaml
"""

import math
import os
import time

from geometry_msgs.msg import TransformStamped, Twist
from georg_sim.world import World
from nav_msgs.msg import Odometry
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan
from tf2_ros import StaticTransformBroadcaster, TransformBroadcaster

DEFAULT_MAP = os.path.join(os.environ.get('GEORG_MAP_DIR', '/root/georg_maps'), 'Nav_Test.yaml')


def _yaw_to_quat(yaw: float):
    return 0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0)


class Sim2D(Node):

    def __init__(self):
        super().__init__('georg_sim')
        p = self.declare_parameter
        self.map_file = p('map_file', DEFAULT_MAP).value
        self.x = p('start_x', 1.0).value
        self.y = p('start_y', 0.1).value
        self.yaw = p('start_yaw', 0.0).value
        # must be smaller than the planner's inflation (grid_rasterizer: 0.25 m),
        # otherwise every small controller deviation ends in a wall
        self.radius = p('robot_radius_m', 0.2).value
        self.cmd_timeout = p('cmd_timeout_s', 0.5).value
        self.beams = p('scan_beams', 360).value
        self.max_range = p('scan_range_m', 12.0).value
        physics_hz = p('physics_hz', 50.0).value
        scan_hz = p('scan_hz', 10.0).value
        self.publish_base_link_tf = p('publish_base_link_tf', True).value

        self.world = World.from_yaml(self.map_file)
        if not self.world.is_free((self.x, self.y), self.radius):
            self.get_logger().warn(f'start pose ({self.x}, {self.y}) is not free')
        self.cmd = Twist()
        self.cmd_time = 0.0
        self.collisions = 0
        self._setup()

        self.create_subscription(Twist, 'cmd_vel', self._on_cmd, 10)
        self.odom_pub = self.create_publisher(Odometry, 'odom', 10)
        self.scan_pubs = [self.create_publisher(LaserScan, topic, qos_profile_sensor_data)
                          for topic in ('merged_scan', 'scan')]
        self.tf = TransformBroadcaster(self)
        self.static_tf = StaticTransformBroadcaster(self)
        self._publish_static()

        self.last_step = time.monotonic()
        self.create_timer(1.0 / physics_hz, self._step)
        self.create_timer(1.0 / scan_hz, self._publish_scan)
        self.get_logger().info(
            f'georg_sim ready: map={self.map_file}, start=({self.x:.2f}, {self.y:.2f}), '
            f'{len(self.world.segments)} wall segments')

    def _setup(self):
        """Prepare the simulation backend (hook for the MuJoCo simulator)."""

    def _command(self, now: float) -> Twist:
        """Return the current command, or zero if it is older than ``cmd_timeout_s``."""
        return self.cmd if now - self.cmd_time <= self.cmd_timeout else Twist()

    def _on_cmd(self, msg: Twist):
        self.cmd = msg
        self.cmd_time = time.monotonic()

    def _step(self):
        now = time.monotonic()
        dt, self.last_step = now - self.last_step, now
        cmd = self._command(now)
        vx, vy, wz = cmd.linear.x, cmd.linear.y, cmd.angular.z
        c, s = math.cos(self.yaw), math.sin(self.yaw)
        nx = self.x + (vx * c - vy * s) * dt
        ny = self.y + (vx * s + vy * c) * dt
        if (nx, ny) != (self.x, self.y) and not self.world.is_free((nx, ny), self.radius):
            self.collisions += 1
            if self.collisions % 50 == 1:
                self.get_logger().warn('collision: step not executed')
            vx = vy = 0.0
        else:
            self.x, self.y = nx, ny
        self.yaw = math.atan2(math.sin(self.yaw + wz * dt), math.cos(self.yaw + wz * dt))
        self._publish_odom(vx, vy, wz)

    def _publish_odom(self, vx, vy, wz):
        stamp = self.get_clock().now().to_msg()
        qx, qy, qz, qw = _yaw_to_quat(self.yaw)
        odom = Odometry()
        odom.header.stamp, odom.header.frame_id = stamp, 'odom'
        odom.child_frame_id = 'base_footprint'
        pose = odom.pose.pose
        pose.position.x, pose.position.y = self.x, self.y
        pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w = \
            qx, qy, qz, qw
        odom.twist.twist.linear.x, odom.twist.twist.linear.y = vx, vy
        odom.twist.twist.angular.z = wz
        self.odom_pub.publish(odom)

        t = TransformStamped()
        t.header.stamp, t.header.frame_id, t.child_frame_id = stamp, 'odom', 'base_footprint'
        t.transform.translation.x, t.transform.translation.y = self.x, self.y
        r = t.transform.rotation
        r.x, r.y, r.z, r.w = qx, qy, qz, qw
        self.tf.sendTransform(t)

    def _publish_static(self):
        if not self.publish_base_link_tf:
            return
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id, t.child_frame_id = 'base_footprint', 'base_link'
        t.transform.rotation.w = 1.0
        self.static_tf.sendTransform(t)

    def _publish_scan(self):
        msg = LaserScan()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        msg.angle_min = -math.pi
        msg.angle_increment = 2 * math.pi / self.beams
        msg.angle_max = msg.angle_min + msg.angle_increment * (self.beams - 1)
        msg.range_min, msg.range_max = 0.1, float(self.max_range)
        msg.scan_time = 0.1
        msg.ranges = [float(r) for r in self._ranges()]
        for pub in self.scan_pubs:
            pub.publish(msg)

    def _ranges(self):
        return self.world.scan(self.x, self.y, self.yaw, self.beams, self.max_range)


def main(args=None):
    rclpy.init(args=args)
    node = Sim2D()
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
