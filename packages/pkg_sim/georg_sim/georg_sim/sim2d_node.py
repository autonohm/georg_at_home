"""2D simulator of Georg (P3, stage 1): same topics as the robot, no physics engine.

Subscribes:  cmd_vel (geometry_msgs/Twist, mecanum: linear.x, linear.y, angular.z)
Publishes:   odom and odom/wheel (nav_msgs/Odometry, frame odom -> base_footprint)
             merged_scan and scan (sensor_msgs/LaserScan, frame base_link, 360 deg)
             tf odom -> base_footprint, tf_static base_footprint -> base_link
             (off with publish_base_link_tf:=false when georg_description publishes it)
             sim/ground_truth (nav_msgs/Odometry): true pose, for tests only
Action:      sim/reset (georg_sim_msgs/ResetSim): back to the start pose, stopped, odometry
             reset; with clear_map also /slam_toolbox/reset (mission sim_reset)
Topics:      sim/set_world (std_msgs/String): load another world (map file name, e.g.
             Arena.yaml): robot at its sim_start, odometry and SLAM map reset;
             sim/world (current world) and sim/worlds (JSON list), both latched
             /clock (rosgraph_msgs/Clock) with publish_clock:=true (nodes with use_sim_time,
             e.g. twist_mux of pkg_drive in sim_mode)

Sensor realism (parameters, defaults = ideal sensors):
  lidar_mode:=robot   two SICK TiM571 at the poses of georg_description (laser1/laser2,
                      270 deg each) -> lidar1/scan, lidar2/scan, and merged_scan like the
                      laser_scan_merger of pkg_slam (base_link, 360 deg, 1 deg, from 0.3 m)
  lidar_noise_m       Gaussian range noise (TiM571: about 0.02 m)
  odom_noise          relative velocity noise of the wheel odometry -> drift (e.g. 0.03)
  cmd_latency_s       commands act this much later (motor controller latency)

The odom frame is aligned with the map frame of the map YAML, so odom positions are
map positions (the task manager uses them as start point for navigation). Commands
older than ``cmd_timeout_s`` stop the robot, like a real motor controller. The robot
does not drive through walls: a step that would collide is not executed.

    ros2 run georg_sim sim2d --ros-args -p map_file:=.../Nav_Test.yaml
"""

import math
import os
import random
import time

from geometry_msgs.msg import TransformStamped, Twist
from georg_sim_msgs.action import ResetSim
from georg_sim import worlds
from georg_sim.world import World
from nav_msgs.msg import Odometry
import rclpy
from rclpy.action import ActionServer
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, qos_profile_sensor_data
from rosgraph_msgs.msg import Clock
from sensor_msgs.msg import LaserScan
from slam_toolbox.srv import Reset as SlamReset
from std_msgs.msg import String
from tf2_ros import StaticTransformBroadcaster, TransformBroadcaster

DEFAULT_MAP = os.path.join(os.environ.get('GEORG_MAP_DIR', '/root/georg_maps'), 'Nav_Test.yaml')


def _yaw_to_quat(yaw: float):
    return 0.0, 0.0, math.sin(yaw / 2.0), math.cos(yaw / 2.0)


def _map_start(path):
    try:
        import yaml
        with open(path, encoding='utf-8') as fh:
            objects = (yaml.safe_load(fh) or {}).get('objects') or {}
        for obj in objects.values():
            if obj.get('type') == 'sim_start':
                return float(obj['position'][0]), float(obj['position'][1])
    except (OSError, ValueError, KeyError, TypeError):
        pass
    return 1.0, 0.1


# mounting poses (x, y, yaw) of laser1_frame / laser2_frame in base_link, georg_description
LIDAR1_POSE = [0.2, -0.155, 5.497787143782138]
LIDAR2_POSE = [-0.2, 0.155, 2.356194490192345]


class Sim2D(Node):

    def __init__(self):
        super().__init__('georg_sim')
        p = self.declare_parameter
        self.map_file = p('map_file', DEFAULT_MAP).value
        self.map_dir = os.path.dirname(os.path.abspath(self.map_file))
        # start: parameters, else the object of type sim_start in the map, else (1.0, 0.1)
        start = _map_start(self.map_file)
        self.x = p('start_x', start[0]).value
        self.y = p('start_y', start[1]).value
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
        self.publish_clock = p('publish_clock', False).value
        self.lidar_mode = p('lidar_mode', 'center').value          # center | robot
        self.lidar_poses = [list(p('lidar1_pose', LIDAR1_POSE).value),
                            list(p('lidar2_pose', LIDAR2_POSE).value)]
        self.lidar_fov = math.radians(p('lidar_fov_deg', 270.0).value)
        self.lidar_beams = p('lidar_beams', 271).value      # 1 deg, like the merged scan
        self.lidar_range = p('lidar_range_m', 25.0).value
        self.lidar_noise = p('lidar_noise_m', 0.0).value
        self.odom_noise = p('odom_noise', 0.0).value
        self.cmd_latency = p('cmd_latency_s', 0.0).value
        self.rng = random.Random(p('random_seed', 7).value)
        # wheel odometry (dead reckoning, drifts with odom_noise), starts at the true pose
        self.ox, self.oy, self.oyaw = self.x, self.y, self.yaw
        self.cmd_queue = []

        self.start_pose = (self.x, self.y, self.yaw)
        self.world = World.from_yaml(self.map_file)
        if not self.world.is_free((self.x, self.y), self.radius):
            self.get_logger().warn(f'start pose ({self.x}, {self.y}) is not free')
        self.cmd = Twist()
        self.cmd_time = 0.0
        self.collisions = 0
        self._setup()

        # best effort: compatible with reliable publishers and with the twist_limiter of
        # pkg_drive, which publishes cmd_vel best effort (a reliable subscription gets nothing)
        self.create_subscription(Twist, 'cmd_vel', self._on_cmd, qos_profile_sensor_data)
        self.odom_pubs = [self.create_publisher(Odometry, topic, 10)
                          for topic in ('odom', 'odom/wheel')]
        self.truth_pub = self.create_publisher(Odometry, 'sim/ground_truth', 10)
        self.clock_pub = self.create_publisher(Clock, '/clock', 10) if self.publish_clock \
            else None
        self.scan_pubs = [self.create_publisher(LaserScan, topic, qos_profile_sensor_data)
                          for topic in ('merged_scan', 'scan')]
        self.lidar_pubs = [self.create_publisher(LaserScan, topic, qos_profile_sensor_data)
                           for topic in ('lidar1/scan', 'lidar2/scan')] \
            if self.lidar_mode == 'robot' else []
        self.tf = TransformBroadcaster(self)
        self.static_tf = StaticTransformBroadcaster(self)
        self._publish_static()

        self.slam_reset = self.create_client(SlamReset, '/slam_toolbox/reset')
        self._reset_server = ActionServer(self, ResetSim, 'sim/reset', self._on_reset)

        # world switch (Lichtblick panel): latched, so late subscribers get the current world
        latched = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL)
        self.world_pub = self.create_publisher(String, 'sim/world', latched)
        self.worlds_pub = self.create_publisher(String, 'sim/worlds', latched)
        self.create_subscription(String, 'sim/set_world', self._on_set_world, 10)
        self._publish_world()

        self.last_step = time.monotonic()
        self.create_timer(1.0 / physics_hz, self._step)
        self.create_timer(1.0 / scan_hz, self._publish_scan)
        self.get_logger().info(
            f'georg_sim ready: map={self.map_file}, start=({self.x:.2f}, {self.y:.2f}), '
            f'{len(self.world.segments)} wall segments, lidar={self.lidar_mode} '
            f'(noise {self.lidar_noise} m), odom noise {self.odom_noise}, '
            f'cmd latency {self.cmd_latency} s, clock {"on" if self.publish_clock else "off"}')

    def _setup(self):
        """Prepare the simulation backend (hook for the MuJoCo simulator)."""

    def _can_switch_world(self):
        """Whether the backend can load another world now (hook for the MuJoCo simulator)."""
        return True

    def _publish_world(self):
        self.world_pub.publish(String(data=os.path.basename(self.map_file)))
        self.worlds_pub.publish(String(data=worlds.worlds_json(self.map_dir)))

    def _on_set_world(self, msg):
        """Load another world: robot at its sim_start, stopped, odometry and SLAM map reset."""
        path = worlds.resolve(msg.data, self.map_dir)
        if path is None:
            self.get_logger().warn(f'set_world: unknown world {msg.data!r} '
                                   f'(choices: {worlds.list_worlds(self.map_dir)})')
            self._publish_world()
            return
        if not self._can_switch_world():
            self.get_logger().warn('set_world: not possible with the MuJoCo viewer open')
            self._publish_world()
            return
        try:
            world = World.from_yaml(path)
        except Exception as exc:  # broken YAML: keep the current world
            self.get_logger().error(f'set_world: cannot load {path}: {exc}')
            self._publish_world()
            return
        self.map_file, self.world = path, world
        sx, sy = _map_start(path)
        self.start_pose = (sx, sy, 0.0)
        self.x, self.y, self.yaw = self.start_pose
        self.ox, self.oy, self.oyaw = self.start_pose
        self.cmd_queue.clear()
        self.cmd, self.cmd_time = Twist(), 0.0
        self._setup()
        if self.slam_reset.service_is_ready():
            self.slam_reset.call_async(SlamReset.Request())
            slam = 'SLAM map reset'
        else:
            slam = 'no /slam_toolbox/reset'
        self._publish_world()
        self.get_logger().info(
            f'world switched to {os.path.basename(path)}: start ({sx:.2f}, {sy:.2f}), '
            f'{len(world.segments)} wall segments, {slam}')

    def _reset_backend(self):
        """Put the backend back to the start pose (hook for the MuJoCo simulator)."""

    async def _on_reset(self, goal_handle):
        """Action sim/reset: start pose, stopped, odometry reset, optionally a fresh map."""
        self.x, self.y, self.yaw = self.start_pose
        self.ox, self.oy, self.oyaw = self.start_pose
        self.cmd_queue.clear()
        self.cmd, self.cmd_time = Twist(), 0.0
        self._reset_backend()
        message = f'robot at the start pose ({self.x:.2f}, {self.y:.2f})'
        ok = True
        if goal_handle.request.clear_map:
            if self.slam_reset.wait_for_service(timeout_sec=2.0):
                response = await self.slam_reset.call_async(SlamReset.Request())
                ok = response is not None and response.result == SlamReset.Response.RESULT_SUCCESS
                message += ', map reset' if ok else ', map reset FAILED'
            else:
                ok = False
                message += ', /slam_toolbox/reset not available'
        self.get_logger().info(f'sim reset: {message}')
        goal_handle.succeed()
        result = ResetSim.Result()
        result.success, result.message = ok, message
        return result

    def _command(self, now: float) -> Twist:
        """Return the current command, or zero if it is older than ``cmd_timeout_s``."""
        # latency: a command acts cmd_latency_s after it arrived
        while self.cmd_queue and self.cmd_queue[0][0] <= now - self.cmd_latency:
            self.cmd_time, self.cmd = self.cmd_queue.pop(0)
            self.cmd_time += self.cmd_latency
        return self.cmd if now - self.cmd_time <= self.cmd_timeout else Twist()

    def _on_cmd(self, msg: Twist):
        self.cmd_queue.append((time.monotonic(), msg))

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

    @staticmethod
    def _odometry(stamp, x, y, yaw, vx, vy, wz):
        qx, qy, qz, qw = _yaw_to_quat(yaw)
        odom = Odometry()
        odom.header.stamp, odom.header.frame_id = stamp, 'odom'
        odom.child_frame_id = 'base_footprint'
        pose = odom.pose.pose
        pose.position.x, pose.position.y = x, y
        pose.orientation.x, pose.orientation.y, pose.orientation.z, pose.orientation.w = \
            qx, qy, qz, qw
        odom.twist.twist.linear.x, odom.twist.twist.linear.y = vx, vy
        odom.twist.twist.angular.z = wz
        return odom

    def _publish_odom(self, vx, vy, wz):
        now = self.get_clock().now()
        stamp = now.to_msg()
        if self.clock_pub is not None:
            self.clock_pub.publish(Clock(clock=stamp))
        self.truth_pub.publish(self._odometry(stamp, self.x, self.y, self.yaw, vx, vy, wz))
        # wheel odometry: integrate the measured (noisy) velocities -> drift like on the robot
        dt = 1.0 / 50.0 if not hasattr(self, '_last_odom') else \
            max(0.0, (now.nanoseconds - self._last_odom) * 1e-9)
        self._last_odom = now.nanoseconds
        if self.odom_noise > 0.0:
            n = self.odom_noise
            vx, vy, wz = (v * (1.0 + self.rng.gauss(0.0, n)) for v in (vx, vy, wz))
            c, s = math.cos(self.oyaw), math.sin(self.oyaw)
            self.ox += (vx * c - vy * s) * dt
            self.oy += (vx * s + vy * c) * dt
            self.oyaw = math.atan2(math.sin(self.oyaw + wz * dt), math.cos(self.oyaw + wz * dt))
        else:
            self.ox, self.oy, self.oyaw = self.x, self.y, self.yaw
        odom = self._odometry(stamp, self.ox, self.oy, self.oyaw, vx, vy, wz)
        for pub in self.odom_pubs:
            pub.publish(odom)

        qx, qy, qz, qw = _yaw_to_quat(self.oyaw)
        t = TransformStamped()
        t.header.stamp, t.header.frame_id, t.child_frame_id = stamp, 'odom', 'base_footprint'
        t.transform.translation.x, t.transform.translation.y = self.ox, self.oy
        r = t.transform.rotation
        r.x, r.y, r.z, r.w = qx, qy, qz, qw
        self.tf.sendTransform(t)

    def _publish_static(self):
        if not self.publish_base_link_tf:
            return
        stamp = self.get_clock().now().to_msg()
        transforms = []
        t = TransformStamped()
        t.header.stamp = stamp
        t.header.frame_id, t.child_frame_id = 'base_footprint', 'base_link'
        t.transform.rotation.w = 1.0
        transforms.append(t)
        if self.lidar_mode == 'robot':
            for i, (lx, ly, lyaw) in enumerate(self.lidar_poses, 1):
                t = TransformStamped()
                t.header.stamp = stamp
                t.header.frame_id, t.child_frame_id = 'base_link', f'laser{i}_frame'
                t.transform.translation.x, t.transform.translation.y = lx, ly
                r = t.transform.rotation
                r.x, r.y, r.z, r.w = _yaw_to_quat(lyaw)
                transforms.append(t)
        self.static_tf.sendTransform(transforms)

    def _noisy(self, r):
        if self.lidar_noise <= 0.0 or not math.isfinite(r):
            return r
        return max(0.0, r + self.rng.gauss(0.0, self.lidar_noise))

    def _publish_scan(self):
        stamp = self.get_clock().now().to_msg()
        if self.lidar_mode == 'robot':
            self._publish_robot_lidars(stamp)
            return
        msg = LaserScan()
        msg.header.stamp = stamp
        msg.header.frame_id = 'base_link'
        msg.angle_min = -math.pi
        msg.angle_increment = 2 * math.pi / self.beams
        msg.angle_max = msg.angle_min + msg.angle_increment * (self.beams - 1)
        msg.range_min, msg.range_max = 0.1, float(self.max_range)
        msg.scan_time = 0.1
        msg.ranges = [float(self._noisy(r)) for r in self._ranges()]
        for pub in self.scan_pubs:
            pub.publish(msg)

    def _publish_robot_lidars(self, stamp):
        """Two 270 deg lidars at their mounting poses, merged like laser_scan_merger."""
        n = self.lidar_beams
        inc = self.lidar_fov / (n - 1)
        c, s = math.cos(self.yaw), math.sin(self.yaw)
        merged_bins = 360
        merged = [math.inf] * merged_bins
        for i, (lx, ly, lyaw) in enumerate(self.lidar_poses):
            ox, oy = self.x + lx * c - ly * s, self.y + lx * s + ly * c
            local = [-self.lidar_fov / 2 + k * inc for k in range(n)]
            ranges = [self._noisy(r) for r in
                      self._rays((ox, oy), [self.yaw + lyaw + a for a in local],
                                 self.lidar_range)]
            msg = LaserScan()
            msg.header.stamp, msg.header.frame_id = stamp, f'laser{i + 1}_frame'
            msg.angle_min, msg.angle_max, msg.angle_increment = local[0], local[-1], inc
            msg.range_min, msg.range_max = 0.05, float(self.lidar_range)
            msg.scan_time = 1.0 / 15.0
            msg.ranges = [float(r) for r in ranges]
            self.lidar_pubs[i].publish(msg)
            # points into base_link, 1 deg bins from -pi, keep the nearest point per bin
            for a, r in zip(local, ranges):
                if not math.isfinite(r) or r < 0.3:
                    continue
                px = lx + r * math.cos(lyaw + a)
                py = ly + r * math.sin(lyaw + a)
                b = int((math.atan2(py, px) + math.pi) / (2 * math.pi) * merged_bins) \
                    % merged_bins
                merged[b] = min(merged[b], math.hypot(px, py))
        msg = LaserScan()
        msg.header.stamp, msg.header.frame_id = stamp, 'base_link'
        msg.angle_increment = 2 * math.pi / merged_bins
        msg.angle_min = -math.pi
        msg.angle_max = msg.angle_min + msg.angle_increment * (merged_bins - 1)
        msg.range_min, msg.range_max = 0.3, float(self.lidar_range)
        msg.scan_time = 1.0 / 15.0
        msg.ranges = [float(r) for r in merged]
        for pub in self.scan_pubs:
            pub.publish(msg)

    def _ranges(self):
        return self.world.scan(self.x, self.y, self.yaw, self.beams, self.max_range)

    def _rays(self, origin, angles, max_range):
        """Ranges from ``origin`` along world ``angles`` (hook for the MuJoCo simulator)."""
        return self.world.raycast_many(origin, angles, max_range)


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
