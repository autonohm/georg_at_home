"""MuJoCo simulator of Georg (P3, stage 2): same topics and parameters as sim2d.

Physics (contacts with walls, inertia of the base) come from MuJoCo, the laser scan
from MuJoCo ray casting. The model is built from the map YAML (georg_sim/mjcf.py).
Runs headless by default; the state is visible in Lichtblick like on the robot.
With ``viewer:=true`` the MuJoCo window opens as well (on macOS the node must run
under ``mjpython``, sim_stack.launch.py does that with ``mujoco_viewer:=true``).

mujoco_ros2_control is not available for macOS, so this node talks to MuJoCo directly.
On Linux the model can later be driven by mujoco_ros2_control instead; the topics
stay the same.

    ros2 run georg_sim simmj --ros-args -p map_file:=.../Nav_Test.yaml
"""

import math
import time

from georg_sim.mjcf import build_mjcf
from georg_sim.sim2d_node import Sim2D
import numpy as np
import rclpy


class SimMuJoCo(Sim2D):

    def _setup(self):
        import mujoco
        self.mj = mujoco
        xml = build_mjcf(self.world, (self.x, self.y, self.yaw), self.radius)
        self.model = mujoco.MjModel.from_xml_string(xml)
        self.data = mujoco.MjData(self.model)
        mujoco.mj_resetDataKeyframe(self.model, self.data, 0)
        mujoco.mj_forward(self.model, self.data)
        self.base_id = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_BODY, 'base')
        self.lidar_site = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_SITE, 'lidar')
        angles = -math.pi + np.arange(self.beams) * (2 * math.pi / self.beams)
        self._beam_angles = angles
        self._geomid = np.zeros(self.beams, dtype=np.int32)
        self._dist = np.zeros(self.beams, dtype=np.float64)
        self.viewer = None
        if self.declare_parameter('viewer', False).value:
            import mujoco.viewer
            self.viewer = mujoco.viewer.launch_passive(self.model, self.data)
            self.viewer.cam.lookat[:] = (self.x, self.y, 0.0)
            self.viewer.cam.distance, self.viewer.cam.elevation = 8.0, -60.0
        self.get_logger().info(
            f'MuJoCo {mujoco.__version__}: {self.model.ngeom} geoms, '
            f'timestep {self.model.opt.timestep}s, viewer {"on" if self.viewer else "off"}')

    def _step(self):
        now = time.monotonic()
        dt, self.last_step = now - self.last_step, now
        cmd = self._command(now)
        c, s = math.cos(self.yaw), math.sin(self.yaw)
        # robot-frame command -> world-frame joint velocities
        self.data.ctrl[:] = [cmd.linear.x * c - cmd.linear.y * s,
                             cmd.linear.x * s + cmd.linear.y * c,
                             cmd.angular.z]
        steps = max(1, min(50, round(dt / self.model.opt.timestep)))
        if self.viewer is not None:
            # the viewer reads model/data in its own thread
            with self.viewer.lock():
                for _ in range(steps):
                    self.mj.mj_step(self.model, self.data)
            if self.viewer.is_running():
                self.viewer.sync()
        else:
            for _ in range(steps):
                self.mj.mj_step(self.model, self.data)
        if self.data.ncon:
            self.collisions += 1
            if self.collisions % 50 == 1:
                self.get_logger().warn('contact with a wall')
        self.x, self.y, yaw = (float(v) for v in self.data.qpos[:3])
        self.yaw = math.atan2(math.sin(yaw), math.cos(yaw))
        vxw, vyw, wz = (float(v) for v in self.data.qvel[:3])
        c, s = math.cos(self.yaw), math.sin(self.yaw)
        self._publish_odom(vxw * c + vyw * s, -vxw * s + vyw * c, wz)

    def _ranges(self):
        origin = np.array(self.data.site_xpos[self.lidar_site], dtype=np.float64)
        a = self._beam_angles + self.yaw
        vec = np.stack([np.cos(a), np.sin(a), np.zeros_like(a)], axis=1).ravel()
        self.mj.mj_multiRay(self.model, self.data, origin, vec, None, True, self.base_id,
                            self._geomid, self._dist, None, self.beams, self.max_range)
        return [d if 0.0 <= d <= self.max_range else math.inf for d in self._dist.tolist()]

    def _rays(self, origin, angles, max_range):
        z = float(self.data.site_xpos[self.lidar_site][2])
        a = np.asarray(angles, dtype=np.float64)
        vec = np.stack([np.cos(a), np.sin(a), np.zeros_like(a)], axis=1).ravel()
        geomid = np.zeros(len(a), dtype=np.int32)
        dist = np.zeros(len(a), dtype=np.float64)
        self.mj.mj_multiRay(self.model, self.data, np.array([origin[0], origin[1], z]), vec,
                            None, True, self.base_id, geomid, dist, None, len(a), max_range)
        return [d if 0.0 <= d <= max_range else math.inf for d in dist.tolist()]


def main(args=None):
    rclpy.init(args=args)
    node = SimMuJoCo()
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
