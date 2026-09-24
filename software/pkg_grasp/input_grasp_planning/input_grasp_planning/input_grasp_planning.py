import threading
import rclpy
from rclpy.node import Node

from std_msgs.msg import String, Float32
from geometry_msgs.msg import Point


class ObjectName(Node):

    def __init__(self):
        super().__init__('object_name')
        self.object_name_publisher_ = self.create_publisher(String, 'object_name', 10)
        self.object_coordinate_publisher_ = self.create_publisher(Point, 'object_coordinates', 10)
        self.object_distance_publisher_ = self.create_publisher(Float32, 'object_distance', 10)

    def publish_name(self, name):
        msg = String()
        msg.data = name
        self.object_name_publisher_.publish(msg)
        self.get_logger().info('Publishing object name: "%s"' % msg.data)

    def publish_coordinates(self, x, y, z):
        msg = Point()
        msg.x = x
        msg.y = y
        msg.z = z
        self.object_coordinate_publisher_.publish(msg)
        self.get_logger().info('Publishing coordinates (%.2f, %.2f, %.2f): ' % (x, y, z))

    def publish_distance(self, distance):
        msg = Float32()
        msg.data = distance
        self.object_distance_publisher_.publish(msg)
        self.get_logger().info('Publishing distance: "%s"' % msg.data)

def calculate_distance(x, y, z):
    return (x**2 + y**2 + z**2) ** 0.5

def keyboard_input_loop(node):
    while rclpy.ok():
        try:
            name = input('Enter object name: ')
            x = float(input('Enter coordinates: x: '))
            y = float(input('Enter coordinates: y: '))
            z = float(input('Enter coordinates: z: '))
        except EOFError:
            break
       
        distance = calculate_distance(x, y, z)

        node.publish_name(name)
        node.publish_coordinates(x, y, z)
        node.publish_distance(distance)


def main(args=None):
    rclpy.init(args=args)

    node = ObjectName()

    # keyboard input
    input_thread = threading.Thread(target=keyboard_input_loop, args=(node,), daemon=True)
    input_thread.start()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()