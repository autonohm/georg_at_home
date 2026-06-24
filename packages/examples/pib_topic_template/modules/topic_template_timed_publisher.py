#!/usr/bin/env python3

import rclpy
import std_msgs.msg

from rclpy.node import Node


class TopicTemplatePublisher(Node):

    # topic publisher construction
    def __init__(self):
        super().__init__('topic_template_publisher')
        # set topic data type and topic name
        self.publisher_ = self.create_publisher(
            std_msgs.msg.String,
            'pib/templates/topic_name', 10
        )
        # set time pause between publications
        timer_period = 0.5 # seconds
        # create timer and link publishing function
        self.timer = self.create_timer(timer_period, self.timer_callback)


    # publishing function, starting after time pause
    def timer_callback(self):
        msg = std_msgs.msg.String()
        msg.data = 'topic_content'
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)


# entry point for topic publisher
def main(args = None):
    rclpy.init(args = args)
    # topic publisher construction
    topic_template_publisher = TopicTemplatePublisher()
    # run topic publisher until rclpy.shutdown()
    rclpy.spin(topic_template_publisher)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    # topic_template_publisher.destroy_node()
    # rclpy.shutdown()


if __name__ == '__main__':
    main()
