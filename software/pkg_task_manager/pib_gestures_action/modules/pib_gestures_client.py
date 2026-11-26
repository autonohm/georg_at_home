#!/usr/bin/env python3

import rclpy
import argparse

from std_msgs.msg import String
from geometry_msgs.msg import Vector3

from rclpy.action import ActionClient
from rclpy.node import Node

from pib_gestures.config import gestures
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

    # create goal message
    def create_goal(
        self,
        pib_gesture,
        vector_x = None,
        vector_y = None,
        vector_z = None,
        pib_side = "none",
        pib_mode = "none",
        pib_hand = "none"
    ):
        
        # goal data types from action/PibGesturesInterface.action
        self.goal_msg = PibGesturesInterface.Goal()
        
        self.goal_msg.has_input_vector = (
            vector_x is not None
            and vector_y is not None
            and vector_z is not None
        )
    
        input_vector = Vector3(
            x = float(vector_x) if vector_x is not None else 0.0,
            y = float(vector_y) if vector_y is not None else 0.0,
            z = float(vector_z) if vector_z is not None else 0.0
        )           

        self.goal_msg.pib_gesture = str(pib_gesture)
        self.goal_msg.input_vector = input_vector
        self.goal_msg.pib_side = str(pib_side)
        self.goal_msg.pib_mode = str(pib_mode)
        self.goal_msg.pib_hand = str(pib_hand)

            

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
            self.get_logger().info(f"Goal rejected")
            # stop action client function, invalid goal
            rclpy.shutdown()
            return

        # self.get_logger().info('Goal accepted')

        # continue action client function and wait for result response
        self._get_result_future = goal_handle.get_result_async()

        # link result response function
        self._get_result_future.add_done_callback(self.get_result_callback)


    # feedback response function, get feedback from action server
    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f"Received feedback: {feedback.status}")
        

    # result response function, get result from action server
    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f"Result: {result.success:d}, {result.message}")
        return result.success
        # stop action client after getting result
        rclpy.shutdown()



'''
This structure provides two different call modes
- call via python code
- call via command line

Call via python code:
Program start_client is executed and the parameters are loaded
start_client handles the client construction, goal creation and sending of goal message

Call via command line:
Program main() is executed and command line parameters are loaded by ArgumentParser 
afterwards main() calls start_client with the parser arguments
'''

def main():
    # Entry point for call via command line
    
    parser = argparse.ArgumentParser(
        description = "pib performs the desired gesture with the given coordinates and configuration"
    )

    parser.add_argument(
        "pib_gesture",
        choices = gestures.pib_gestures.keys(),
        metavar = "pib_gesture",
        help = "Gesture to perform",
    )
    
    # first argument is required for validating pib_mode afterwards
    # pib_mode must fit pib_gesture
    args, remaining = parser.parse_known_args()

    parser.add_argument(
        "--x",
        type = float,
        help = "X coordinate of the object"
    )

    parser.add_argument(
        "--y",
        type = float,
        help = "Y coordinate of the object"
    )

    parser.add_argument(
        "--z",
        type = float,
        help = "Z coordinate of the object"
    )

    parser.add_argument(
        "--pib_side",
        choices = gestures.pib_side.keys(),
        default = "none",
        help = "Side for the gesture",
    )

    parser.add_argument(
        "--pib_mode",
        choices = gestures.pib_gesture_modes[args.pib_gesture].keys(),
        default = "none",
        help = "Mode for the gesture",
    )

    parser.add_argument(
        "--pib_hand",
        choices = gestures.pib_hand[args.pib_gesture].keys(),
        default = "none",
        help = "Hand configuration to use",
    )
    
    args = parser.parse_args()

    start_client(
        args.pib_gesture,
        args.x,
        args.y,
        args.z,
        args.pib_side,
        args.pib_mode,
        args.pib_hand
    )

def start_client(
    pib_gesture,
    vector_x = None,
    vector_y = None,
    vector_z = None,
    pib_side = "none",
    pib_mode = "none",
    pib_hand = "none"
):
    
    # entry point for call via python code

    rclpy.init(args = None)
    # action client construction
    pib_gestures_client = ActionTemplateClient()
        
    # create goal content from sys.argv)
    pib_gestures_client.create_goal(
        pib_gesture,
        vector_x,
        vector_y,
        vector_z,
        pib_side,
        pib_mode,
        pib_hand
    )

    # send goal after action client construction
    pib_gestures_client.send_goal(pib_gestures_client.goal_msg)
    
    # run action client until rclpy.shutdown()
    rclpy.spin(pib_gestures_client)
    
    # shut down the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    # pib_gestures_client.destroy_node()
    # rclpy.shutdown()



if __name__ == '__main__':
    # execution via command line
    main()
