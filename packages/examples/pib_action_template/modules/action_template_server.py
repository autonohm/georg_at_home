#!/usr/bin/env python3

import rclpy
import std_msgs.msg
from rclpy.action import ActionServer, GoalResponse
from rclpy.node import Node

from pib_action_template.action import Template # interface with data types

# import your core function here
# from my_package.my_function import main

class ActionTemplateServer(Node):

    # action server construction
    def __init__(self):
        super().__init__('action_template_server')
        self._action_server = ActionServer(
            self, Template, 'template',
            execute_callback = self.execute_callback,
            goal_callback = self.goal_callback
        )
        self._goal_running = False

    # goal received from action client
    # function executed right after receiving goal but before execution
    def goal_callback(self, goal_request):
        # validating goal content is in accepted range
        if not goal_request.goal_content == 'goal_content':
            return GoalResponse.REJECT

        # if only accepting one goal at a time
        if self._goal_running:
            return GoalResponse.REJECT
        else:
            return GoalResponse.ACCEPT


    # execution function
    # executed after acccepting goal
    def execute_callback(self, goal_handle):
        self.get_logger().info('Executing goal...')

        # starting execution
        self.goal_running = True

        # feedback data types from action/Template.action
        feedback_msg = Template.Feedback()
        feedback_msg.feedback_content = 'feedback_content'

        # feedback to action client feedback response function
        goal_handle.publish_feedback(feedback_msg)

        # result data types from action/Template.action
        result = Template.Result()

        try:
            # here starts the execution of the core functionality
            # replace this line with the call of your function(s) from import
            # result.result_content = my_function.main()
            result.result_content = 'result = goal(' + goal_handle.request.goal_content + ')'

            # successful execution
            goal_handle.succeed()

        # error in execution of my_function
        except Exception as e:
            error_string = 'error in myfuncion.main'
            result.result_content = f"error: {error_string}"
            goal_handle.abort()

        # client canceling execution
        if goal_handle.is_cancel_requested:
            result.result_content = 'client canceled request'
            goal_handle.canceled()

        # finished execution
        self._goal_running = False

        # return to action client result response function
        return result


# entry point for action server
def main(args = None):
    rclpy.init(args = args)

    # action server construction
    action_template_server = ActionTemplateServer()

    # run action client until rclpy.shutdown()
    rclpy.spin(action_template_server)

    # shut down the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    # topic_template_subscriber.destroy_node()
    # rclpy.shutdown()

if __name__ == '__main__':
    main()
