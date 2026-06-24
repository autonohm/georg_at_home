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


    # publishing function
    def trigger_callback(self):
        msg = std_msgs.msg.String()
        msg.data = 'topic_content'
        self.publisher_.publish(msg)
        self.get_logger().info('Publishing: "%s"' % msg.data)


# entry point for topic publisher
def main(args = None):
    rclpy.init(args = args)
    # topic publisher construction
    topic_template_publisher = TopicTemplatePublisher()
    
    # publish once
    topic_template_publisher.trigger_callback()

    # shutdown the node explicitly
    topic_template_publisher.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
