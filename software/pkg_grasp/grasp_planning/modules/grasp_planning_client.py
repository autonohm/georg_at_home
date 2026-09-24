#!/usr/bin/env python3
import subprocess
import sys
import rclpy
import std_msgs.msg
from rclpy.action import ActionClient
from rclpy.node import Node

from std_msgs.msg import String, Float32
from geometry_msgs.msg import Point

from grasp_planning.action import GraspPlanning # interface with data types

class GraspPlanner(Node):

    # action client construction
    def __init__(self):
        super().__init__('GraspPlanner')
        self._action_client = ActionClient(self, GraspPlanning, 'grasp_planning')

        # path to D(R, O) Grasp
        self.declare_parameter('script_path', '/home/athome/DRO-Gym/validate.py')

        # Cache for object information
        self.object_name = None
        self.object_coordinates = None
        self.object_distance = None

        self.which_hand = None

        # subscriber for object information
        self.object_name_subscriber = self.create_subscription(String, 'object_name', self.object_name_callback, 10)
        self.object_coordinates_subscriber = self.create_subscription(Point, 'object_coordinates', self.object_coordinates_callback, 10)
        self.object_distance_subscriber = self.create_subscription(Float32, 'object_distance', self.object_distance_callback, 10)

    def object_name_callback(self, msg):
        self.object_name = msg.data
        self.get_logger().info(f'Received object_name: {self.object_name}')
        self.try_send_goal()

    def object_coordinates_callback(self, msg):
        self.object_coordinates = msg
        self.get_logger().info(f'Received object_coordinates: {self.object_coordinates}')
        self.try_send_goal()

    def object_distance_callback(self, msg):
        self.object_distance = msg.data
        self.get_logger().info(f'Received object_distance: {self.object_distance}')
        self.try_send_goal()

    def try_send_goal(self):
        if self.object_name is None or self.object_coordinates is None or self.object_distance is None:
            self.get_logger().info('Waiting for object information.')
            return
        elif self.object_distance < 0 or self.object_distance > 0.6:
            self.get_logger().info('Object is out of reach. Consider repositioning.')
            return
        if self.object_coordinates.y < 0:
            self.which_hand = 'pib_l'
            self.get_logger().info('Object is to the left - using left hand to grasp. Will return since the left hand isn`t included in the grasp model yet.')
            return
        elif self.object_coordinates.y >= 0:
            #self.which_hand = 'pib_r'
            self.which_hand = 'shadowhand'
            self.get_logger().info('Object is to the right - using right hand for grasp.')
        self.send_goal('goal_content', self.object_name, self.object_coordinates, self.object_distance, self.which_hand)

    # send goal to server to initiate action execution
    def send_goal(self, goal_content, object_name, object_coordinates, object_distance, which_hand):
        # goal data types from action/GraspPlanning.action
        goal_msg = GraspPlanning.Goal()
        # set goal content
        goal_msg.goal_content = goal_content
        goal_msg.script_path = self.get_parameter('script_path').value
        goal_msg.object_name = object_name
        goal_msg.object_coordinates = object_coordinates
        goal_msg.object_distance = object_distance
        goal_msg.which_hand = which_hand

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
            #rclpy.shutdown()
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
        self.get_logger().info('Result: {0}'.format(result.result_content))
        # stop action client after getting result
        rclpy.shutdown()



# entry point for action client
def main(args = None):
    rclpy.init(args = args)
    # action client construction
    action_client = GraspPlanner()

    # send goal after action client construction
    #action_client.send_goal('goal_content')
    
    # run action client until rclpy.shutdown()
    rclpy.spin(action_client)
    
    # shut down the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    # topic_template_subscriber.destroy_node()
    # rclpy.shutdown()


if __name__ == '__main__':
    main()

