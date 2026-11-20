#!/usr/bin/env python3

import rclpy
import std_msgs.msg

from std_msgs.msg import Empty
from rclpy.action import ActionClient
from rclpy.node import Node

from pib_action_template.action import Template # interface with data types

class ActionTemplateClient(Node):

    # action client construction
    def __init__(self):
        super().__init__('action_template_client')
        self._action_client = ActionClient(
            self,
            Template,
            'template'
        )
        
        # create subscriber for restart
        self._trigger_sub = self.create_subscription(
            Empty,
            'start_next_goal',
            self.trigger_callback,
            10
        )


    # send goal to server to initiate action execution
    def send_goal(self, goal_content):
        # goal data types from action/Template.action
        goal_msg = Template.Goal()
        # set goal content
        goal_msg.goal_content = goal_content

        self._action_client.wait_for_server()

        # send goal to action server and link feedback response function
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg, feedback_callback = self.feedback_callback
        )

        # link goal response function for goal validation
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    
    # response from action server, goal is accepted or rejected
    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            # stop action client function, invalid goal
            rclpy.shutdown()
            return

        self.get_logger().info('Goal accepted')

        # continue action client function and wait for result response
        self._get_result_future = goal_handle.get_result_async()

        # link result response function
        self._get_result_future.add_done_callback(self.get_result_callback)


    # feedback response function, get feedback from action server
    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info('Received feedback: {0}'.format(feedback.feedback_content))
        

    # result response function, get result from action server
    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info('Result: {0}\n'.format(result.result_content))
        

    def trigger_callback(self, msg):
        self.get_logger().info('Trigger vom Server erhalten -> neues Goal')
        self.send_goal('goal_content')


# entry point for action client
def main(args = None):
    rclpy.init(args = args)
    # action client construction
    action_client = ActionTemplateClient()

    # send goal after action client construction
    action_client.send_goal('goal_content')
    
    # run action client until rclpy.shutdown()
    rclpy.spin(action_client)
    
    # shut down the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    # topic_template_subscriber.destroy_node()
    # rclpy.shutdown()


if __name__ == '__main__':
    main()

