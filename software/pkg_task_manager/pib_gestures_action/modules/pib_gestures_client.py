#!/usr/bin/env python3

import rclpy
import sys
from std_msgs.msg import String
from geometry_msgs.msg import Vector3

from rclpy.action import ActionClient
from rclpy.node import Node

from pib_gestures.src.pib_gestures.config import gestures
from pib_gestures_action.action import PibGesturesInterface # interface with data types

class ActionTemplateClient(Node):

    # action client construction
    def __init__(self):
        super().__init__('pib_gestures_client')
        self._action_client = ActionClient(
            self,
            PibGesturesInterface,
            'pib_gestures_interface'
        )
        
    
    def create_goal(self):
        # goal data types from action/PibGesturesInterface.action
        goal_msg = PibGesturesInterface.Goal()
        
        # create goal message
        self.goal_msg = PibGesturesInterface.Goal()
        self.goal_msg.gesture = str(sys.argv[1])
        self.goal_msg.camera_vector.x = float(sys.argv[2])
        self.goal_msg.camera_vector.y = float(sys.argv[3])
        self.goal_msg.camera_vector.z = float(sys.argv[4])      
    
        if len(sys.argv) > 5:
            self.goal_msg.pib_side = sys.argv[5]
            if goal_msg.pib_side not in gestures.pib_side.keys():
                usage_info()
                print("pointing side", self.goal_msg.pib_side)
                raise ValueError("pib side is faulty")
        else:
            self.goal_msg.pib_side = gestures.pib_side['none']
        
        if len(sys.argv) > 6:
            self.goal_msg.pib_gesture = sys.argv[6]
            if self.goal_msg.pib_gesture not in gestures.pib_gesture.keys():
                usage_info()
                print("pointing mode:", self.goal_msg.pib_gesture)
                raise ValueError("pib gesture is faulty")
        else:
            self.goal_msg.pib_gesture = gestures.pib_gesture['none']
            
        if len(sys.argv) > 7:
            self.goal_msg.pib_hand = sys.argv[7]
            if self.goal_msg.pib_hand not in gestures.pib_hand.keys():
                usage_info()
                print("pointing gesture:", self.goal_msg.pib_hand)
                raise ValueError("pib hand is faulty")
        else:
            self.goal_msg.pib_hand = gestures.pib_hand['none']

        

    # send goal to server to initiate action execution
    def send_goal(self, goal):
        self._action_client.wait_for_server()

        # send goal to action server and link feedback response function
        self._send_goal_future = self._action_client.send_goal_async(
            self.goal_msg, feedback_callback = self.feedback_callback
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
        self.get_logger().info('Received feedback: {0}'.format(feedback.status))
        

    # result response function, get result from action server
    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info('Result: {0}'.format(result.success))
        # stop action client after getting result
        rclpy.shutdown()



def usage_info():
    print("Usage: python3.9 point_to.py x_value y_value z_value pib_side pib_gesture pib_hand\n")
    print("Required values are in float: x value, y value, z value\n")
    print("Optional values are:")
    print("pib_side in", gestures.pib_side.keys())
    print("pib_gesture in", gestures.pib_gesture.keys())
    print("pib_hand in", gestures.pib_hand.keys())
    print("global coordinate system, adapted to ros and onshape configuration:")
    print("x axis pointing against pib, y axis pointing to pibs right side, z axis pointing upwards\n")
    print("usage example: python3.9 point_to.py -1000 500 -200 right bent_arm index_finger")



def main(args = None):
    rclpy.init(args = args)
    # action client construction
    action_client = ActionTemplateClient()
    
    if len(sys.argv) < 4 or len(sys.argv) > 7:
        print("Faulty parameter count")
        usage_info()
        sys.exit()
        
    # create goal content from sys.argv)
    action_client.create_goal()

    # send goal after action client construction
    action_client.send_goal(action_client.goal_msg)
    
    # run action client until rclpy.shutdown()
    rclpy.spin(action_client)
    
    # shut down the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    # topic_template_subscriber.destroy_node()
    # rclpy.shutdown()



if __name__ == '__main__':
    main()

