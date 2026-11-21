"""pib_model node: shows the movable pib on Georg in Lichtblick.

    /joint_states  (sensor_msgs/JointState, motor names, centidegrees; pib-backend or the
                    fake motors in sim)  ->  pib/joint_states (URDF joint names, rad)
    static tf      pib_waist_link -> root (mount of the pib model on Georg)
    /robot_description (Georg, pkg_urdf)  ->  /georg_full/robot_description
                    (Georg without the rigid pib mesh + movable pib, for Lichtblick)

robot_state_publisher (namespace pib, see config/pib_model.launch.py) publishes the tf of the
pib links from pib/joint_states. Georg's own /joint_states (wheels) are ignored here.
"""
import json
import math
import os

from geometry_msgs.msg import TransformStamped
import rclpy
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from sensor_msgs.msg import JointState
from std_msgs.msg import String
from tf2_ros import StaticTransformBroadcaster

from pib_model.description import combine
from pib_model.mapping import MotorMapping

LATCHED = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                     reliability=ReliabilityPolicy.RELIABLE)


def _quaternion(roll, pitch, yaw):
    cr, sr = math.cos(roll / 2), math.sin(roll / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    return (sr * cp * cy - cr * sp * sy, cr * sp * cy + sr * cp * sy,
            cr * cp * sy - sr * sp * cy, cr * cp * cy + sr * sp * sy)


class PibModelNode(Node):
    """Joint state conversion, mount tf and combined description."""

    def __init__(self):
        """Read the model files and set up topics."""
        super().__init__('pib_model')
        p = self.declare_parameter
        model_dir = p('model_dir', '').value
        if not model_dir:
            from ament_index_python.packages import get_package_share_directory
            model_dir = os.path.join(get_package_share_directory('pib_model'), 'model')
        self.waist = p('waist_link', 'pib_waist_link').value
        # mount of the pib model on Georg: estimated from the bounding boxes of the rigid
        # pib_4S.stl of georg_description (head top and shoulders), see README; tune here
        self.xyz = list(p('mount_xyz', [0.103, 0.065, 0.613]).value)
        self.rpy = list(p('mount_rpy', [0.0, 0.0, math.pi / 2]).value)
        self.hide_mesh = p('hide_mesh', 'pib_4S.stl').value
        # head camera (OAK) on the head link, same frame id as pib-backend's camera images;
        # position from the face of the pib model (front, upper middle), looking forward
        self.camera_link = p('camera_link', 'a81_motor_shaft').value
        self.camera_frame = p('camera_frame', 'oak_rgb_camera_optical_frame').value
        self.camera_xyz = list(p('camera_xyz', [0.0415, -0.0504, 0.0796]).value)
        self.camera_rpy = list(p('camera_rpy', [-math.pi / 2, 0.0, -math.pi]).value)
        with open(os.path.join(model_dir, 'mapping.json'), encoding='utf-8') as f:
            self.mapping = MotorMapping(json.load(f))
        with open(os.path.join(model_dir, 'pib.urdf'), encoding='utf-8') as f:
            self.pib_urdf = f.read()
        self.motors = {m: 0.0 for m in self.mapping.motor_names}

        self.joint_pub = self.create_publisher(JointState, 'pib/joint_states', 10)
        self.full_pub = self.create_publisher(String, 'georg_full/robot_description', LATCHED)
        self.create_subscription(JointState, 'joint_states', self._on_motor_states, 10)
        self.create_subscription(String, 'robot_description', self._on_georg, LATCHED)
        self.static_tf = StaticTransformBroadcaster(self)
        self._publish_mount()
        # robot_state_publisher needs every movable joint, also before pib-backend answers
        self.create_timer(0.1, self._publish_joints)
        self.get_logger().info(f'pib model ready: {len(self.motors)} motors, mount '
                               f'{self.waist} -> root xyz={self.xyz} rpy={self.rpy}')

    def _static(self, parent, child, xyz, rpy):
        t = TransformStamped()
        t.header.stamp = self.get_clock().now().to_msg()
        t.header.frame_id, t.child_frame_id = parent, child
        t.transform.translation.x, t.transform.translation.y, t.transform.translation.z = xyz
        (t.transform.rotation.x, t.transform.rotation.y, t.transform.rotation.z,
         t.transform.rotation.w) = _quaternion(*rpy)
        return t

    def _publish_mount(self):
        self.static_tf.sendTransform([
            self._static(self.waist, 'root', self.xyz, self.rpy),
            self._static(self.camera_link, self.camera_frame, self.camera_xyz, self.camera_rpy),
        ])

    def _on_motor_states(self, msg):
        for name, value in zip(msg.name, msg.position):
            if name in self.motors:
                self.motors[name] = value

    def _publish_joints(self):
        positions = self.mapping.joint_positions(self.motors)
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(positions)
        msg.position = [positions[n] for n in msg.name]
        self.joint_pub.publish(msg)

    def _on_georg(self, msg):
        try:
            full = combine(msg.data, self.pib_urdf, self.waist, 'root', self.xyz, self.rpy,
                           self.hide_mesh)
        except Exception as exc:  # noqa: BLE001 - keep running, log the reason
            self.get_logger().error(f'cannot combine the robot descriptions: {exc}')
            return
        self.full_pub.publish(String(data=full))
        self.get_logger().info('published georg_full/robot_description (Georg + pib)')


def main():
    """Run the node."""
    rclpy.init()
    node = PibModelNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
