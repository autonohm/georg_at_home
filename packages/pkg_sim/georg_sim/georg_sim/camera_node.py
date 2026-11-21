"""Simulated head camera of Georg (profile sim): what the robot would see in the simulation.

Renders the simulated world (walls of the map YAML, georg_sim/mjcf.py) with MuJoCo on the GPU
(MUJOCO_GL=egl) from the pose of the real head camera:

    pose = /sim/ground_truth (base_footprint in the world)
           * tf base_footprint -> oak_rgb_camera_optical_frame (georg_description + pib model,
             follows the head motors)

Publishes like pib-backend's camera node, so Lichtblick and the task manager see no difference:
    /oak/rgb/image_raw/compressed (sensor_msgs/CompressedImage, jpeg), frame
    oak_rgb_camera_optical_frame

    ros2 run georg_sim sim_camera --ros-args -p map_file:=.../Nav_Test.yaml
"""

import io
import math
import os

from georg_sim.mjcf import build_mjcf
from georg_sim.world import World
from nav_msgs.msg import Odometry
import numpy as np
from PIL import Image
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from rclpy.time import Time
from sensor_msgs.msg import CompressedImage
import tf2_ros

DEFAULT_MAP = os.path.join(os.environ.get('GEORG_MAP_DIR', '/root/georg_maps'), 'Nav_Test.yaml')


VISUALS = """
  <visual>
    <headlight ambient="0.35 0.35 0.35" diffuse="0.5 0.5 0.5" specular="0 0 0"/>
    <quality shadowsize="2048"/>
  </visual>
  <asset>
    <texture name="sky" type="skybox" builtin="gradient" rgb1="0.75 0.85 0.95"
             rgb2="0.95 0.95 0.97" width="256" height="256"/>
    <texture name="tiles" type="2d" builtin="checker" rgb1="0.82 0.78 0.72"
             rgb2="0.72 0.68 0.62" width="512" height="512"/>
    <material name="floor" texture="tiles" texrepeat="20 20"/>
  </asset>
"""


def add_visuals(xml):
    """Light, sky and a tiled floor for the camera image (physics stay the same)."""
    xml = xml.replace('<compiler angle="radian"/>', '<compiler angle="radian"/>' + VISUALS, 1)
    xml = xml.replace('rgba="0.9 0.9 0.9 1"/>', 'material="floor"/>', 1)
    xml = xml.replace('<worldbody>', '<worldbody>\n    <light pos="4 0 6" dir="0 0 -1" '
                      'diffuse="0.6 0.6 0.6" castshadow="false"/>', 1)
    return xml.replace('rgba="0.6 0.6 0.65 1"', 'rgba="0.93 0.93 0.9 1"')


def add_meshes(xml, visuals_file):
    """Insert the furniture meshes of the arena and hide the box walls of the 2D map."""
    import re
    with open(visuals_file, encoding='utf-8') as fh:
        snippet = fh.read()
    assets = re.search(r'<asset>(.*?)</asset>', snippet, re.S).group(1)
    geoms = re.search(r'<worldbody>(.*?)</worldbody>', snippet, re.S).group(1)
    meshdir = os.path.dirname(os.path.abspath(visuals_file))
    xml = xml.replace('<compiler angle="radian"/>',
                      f'<compiler angle="radian" meshdir="{meshdir}"/>', 1)
    xml = xml.replace('</asset>', assets + '</asset>', 1)
    xml = xml.replace('<worldbody>', '<worldbody>' + geoms, 1)
    return re.sub(r'(<geom name="wall\d+"[^>]*?)rgba="[^"]*"', r'\1rgba="0 0 0 0"', xml)


def _quat_to_matrix(x, y, z, w):
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def free_camera(position, forward):
    """MuJoCo free camera (lookat, distance, azimuth, elevation) for a position and direction."""
    f = np.asarray(forward, dtype=float)
    f /= np.linalg.norm(f)
    azimuth = math.degrees(math.atan2(f[1], f[0]))
    elevation = math.degrees(math.asin(max(-1.0, min(1.0, f[2]))))
    distance = 1.0
    lookat = np.asarray(position, dtype=float) + f * distance
    return lookat, distance, azimuth, elevation


class SimCamera(Node):
    """Renders the head camera image from the simulated world."""

    def __init__(self):
        """Build the MuJoCo world and start the render timer."""
        super().__init__('sim_camera')
        p = self.declare_parameter
        map_file = p('map_file', DEFAULT_MAP).value
        self.width = p('width', 640).value
        self.height = p('height', 360).value
        hfov = math.radians(p('hfov_deg', 69.0).value)          # OAK-D colour camera
        rate = p('rate_hz', 10.0).value                          # like the real camera
        self.frame = p('camera_frame', 'oak_rgb_camera_optical_frame').value
        self.base_frame = p('base_frame', 'base_footprint').value
        self.quality = p('jpeg_quality', 80).value
        # MJCF snippet with the real furniture meshes (pkg_sim/tools/arena_convert.py); the
        # box walls of the map are hidden then
        visuals = p('visuals_file', '').value

        import mujoco
        self.mj = mujoco
        world = World.from_yaml(map_file)
        xml = add_visuals(build_mjcf(world, (0.0, 0.0, 0.0), 0.2))
        if visuals and os.path.exists(visuals):
            xml = add_meshes(xml, visuals)
        self.model = mujoco.MjModel.from_xml_string(xml)
        self.data = mujoco.MjData(self.model)
        # the robot's own simulated body is not part of the camera image
        base = mujoco.mj_name2id(self.model, mujoco.mjtObj.mjOBJ_GEOM, 'base')
        if base >= 0:
            self.model.geom_rgba[base][3] = 0.0
        vfov = 2 * math.atan(math.tan(hfov / 2) * self.height / self.width)
        self.model.vis.global_.fovy = math.degrees(vfov)
        mujoco.mj_forward(self.model, self.data)
        self.renderer = mujoco.Renderer(self.model, self.height, self.width)
        self.camera = mujoco.MjvCamera()
        self.camera.type = mujoco.mjtCamera.mjCAMERA_FREE

        self.base_pose = None
        self.create_subscription(Odometry, 'sim/ground_truth', self._on_truth, 10)
        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.pub = self.create_publisher(CompressedImage, '/oak/rgb/image_raw/compressed',
                                         qos_profile_sensor_data)
        self.create_timer(1.0 / rate, self._render)
        self._warned = False
        self.get_logger().info(
            f'sim camera ready: {self.width}x{self.height} @ {rate} Hz, hfov '
            f'{math.degrees(hfov):.0f} deg, frame {self.frame}, map {map_file}')

    def _on_truth(self, msg):
        p, q = msg.pose.pose.position, msg.pose.pose.orientation
        self.base_pose = (np.array([p.x, p.y, p.z]), _quat_to_matrix(q.x, q.y, q.z, q.w))

    def _camera_in_world(self):
        try:
            tf = self.tf_buffer.lookup_transform(self.base_frame, self.frame, Time())
        except (tf2_ros.LookupException, tf2_ros.ConnectivityException,
                tf2_ros.ExtrapolationException) as exc:
            if not self._warned:
                self.get_logger().warn(f'no tf {self.base_frame} -> {self.frame} yet: {exc}')
                self._warned = True
            return None
        t, r = tf.transform.translation, tf.transform.rotation
        cam_pos = np.array([t.x, t.y, t.z])
        cam_rot = _quat_to_matrix(r.x, r.y, r.z, r.w)
        base_pos, base_rot = self.base_pose
        position = base_pos + base_rot @ cam_pos
        forward = base_rot @ cam_rot @ np.array([0.0, 0.0, 1.0])   # optical z = viewing axis
        return position, forward

    def _render(self):
        if self.base_pose is None:
            return
        pose = self._camera_in_world()
        if pose is None:
            return
        lookat, distance, azimuth, elevation = free_camera(*pose)
        self.camera.lookat[:] = lookat
        self.camera.distance, self.camera.azimuth = distance, azimuth
        self.camera.elevation = elevation
        self.renderer.update_scene(self.data, camera=self.camera)
        pixels = self.renderer.render()
        buf = io.BytesIO()
        Image.fromarray(pixels).save(buf, format='JPEG', quality=self.quality)
        msg = CompressedImage()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame
        msg.format = 'jpeg'
        msg.data = buf.getvalue()
        self.pub.publish(msg)


def main(args=None):
    """Run the node."""
    rclpy.init(args=args)
    node = SimCamera()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        # skip the EGL clean-up of MuJoCo, which raises errors at interpreter exit
        os._exit(0)


if __name__ == '__main__':
    main()
