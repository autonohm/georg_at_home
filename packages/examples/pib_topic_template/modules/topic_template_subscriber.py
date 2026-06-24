#!/usr/bin/env python3

import rclpy
import std_msgs.msg

from rclpy.node import Node


class TopicTemplateSubscriber(Node):

    # topic subscriber construction
    def __init__(self):
        super().__init__('topic_template_subscriber')
        # set topic data type, topic name and publish response function
        self.subscription = self.create_subscription(
            std_msgs.msg.String, 'pib/templates/topic_name',
            self.subscriber_callback, 10
        )
        self.subscription  # prevent unused variable warning


    # publsih response function
    def subscriber_callback(self, msg):
        self.get_logger().info('receiving topic content: "%s"' % msg.data)


# entry point for topic subscriber
def main(args = None):
    rclpy.init(args = args)
    # topic subscriber construction
    topic_template_subscriber = TopicTemplateSubscriber()
    
    # run topic subscriber until rclpy.shutdown()
    rclpy.spin(topic_template_subscriber)

    # shut down the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    # topic_template_subscriber.destroy_node()
    # rclpy.shutdown()


if __name__ == '__main__':
    main()
