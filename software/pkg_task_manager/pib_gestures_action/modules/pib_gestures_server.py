#!/usr/bin/env python3

import rclpy

from std_msgs.msg import String
from geometry_msgs.msg import Vector3
# import georg_msgs.msg

from rclpy.action import ActionServer, GoalResponse
from rclpy.node import Node

# import your core function here
from pib_gestures_action.action import PibGesturesInterface # interface with data types
from pib_gestures.config.gestures import pib_gestures, pib_side, pib_gesture_modes, pib_hand
from pib_gestures.geometry import Object_Vector
from pib_gestures.core import *

class PibGesturesServer(Node):

    # action server construction
    def __init__(self):
        super().__init__('pib_gestures_server')
        self._action_server = ActionServer(
            self,
            PibGesturesInterface,
            'pib_gestures_interface',
            execute_callback = self.execute_callback,
            goal_callback = self.goal_callback
        )
        self._goal_running = False

    
    # goal received from action client
    # function executed right after receiving goal but before execution
    def goal_callback(self, goal_handle):
        # goal validation
        try:
            # if only accepting one goal at a time
            if self._goal_running:
                raise RuntimeError("Action already running")

            if goal_handle.pib_gesture not in pib_gestures.keys():
                raise ValueError(f"faulty pib_gesture selection: gesture <{goal_handle.pib_gesture}> not defined")

            if goal_handle.pib_side not in pib_side.keys():
                raise ValueError(f"faulty pib_side selection: side <{goal_handle.pib_side}> not defined")

            if goal_handle.pib_mode not in pib_gesture_modes[goal_handle.pib_gesture].keys():
                raise ValueError(f"faulty pib_mode selection: gesture mode <{goal_handle.pib_mode}> does not fit gesture <{goal_handle.pib_gesture}>")

            if goal_handle.pib_hand not in pib_hand.keys():
                raise ValueError(f"faulty pib_hand selection: hand <{goal_handle.pib_hand}> is not defined")

            if not self.parameters_complete(goal_handle):
                raise ValueError(f"Missing parameters for gesture <{goal_handle.pib_gesture}>")

        except Exception as error_message:
            self.get_logger().error(f"Goal rejected: {error_message}")
            return GoalResponse.REJECT

        self._goal_running = True
        return GoalResponse.ACCEPT


    # execution function
    # executed after acccepting goal
    def execute_callback(self, goal_handle):
        # self.get_logger().info('starting execution')
                
        # result data types from action/PibGesturesInterface.action
        result = PibGesturesInterface.Result()

        try:            
            # build function call with parameter dictionary 
            params = {}
            
            match goal_handle.request.pib_gesture:
                case "look_at" | "locate_object":
                    params["object_vector"] = self.create_object_vector(goal_handle.request.input_vector)

                case "point_to":
                    params["object_vector"] = self.create_object_vector(goal_handle.request.input_vector)
                    params["pib_side"] = goal_handle.request.pib_side
                    params["pib_mode"] = goal_handle.request.pib_mode
                    params["pib_hand"] = goal_handle.request.pib_hand

                case "greet_person":
                    params["object_vector"] = self.create_object_vector(goal_handle.request.input_vector)
                    params["pib_side"] = goal_handle.request.pib_side
                    params["pib_mode"] = goal_handle.request.pib_mode
                
                case "offer_hand":
                    params["pib_side"] = goal_handle.request.pib_side
                    params["pib_mode"] = goal_handle.request.pib_mode
                    
                case "go_rest":
                    params["pib_mode"] = goal_handle.request.pib_mode

                case "open_hand" | "close_hand":
                    params["pib_side"] = goal_handle.request.pib_side
                    
                # case "face_follow":
                #    params["gain"] = 0.5

                case _:
                    raise ValueError(f"faulty gesture selection: gesture <{self.goal.pib_gesture}> not defined")

            # call core functionality
            
            # self.get_logger().info('starting execution')

            result.success = self.gesture_functions[goal_handle.request.pib_gesture](params)

            # self.get_logger().info('finished execution')

                # exception in execution
        except Exception as error_message:
            result.success = -1
            # self.get_logger().error(f"exeption occured: {error_message}")
            result.message = str(error_message)
            goal_handle.abort()
            self._goal_running = False
            return result
            
        # client canceling execution
        if goal_handle.is_cancel_requested:
            result.success = 2
            # self.get_logger().error('cancel request from client')
            result.message = f"client canceled request"
            goal_handle.canceled()

        # successful execution
        elif result.success == 0:
            result.message = f"executed successfully"
            # self.get_logger().info('successful execution')
            goal_handle.succeed()
            
        elif result.success == 1:
            result.message = f"calculated joint angles out of limits"
            # self.get_logger().info('execution results in joint angles out of limits')
            goal_handle.abort()
            
        # finished execution
        self._goal_running = False

        # self.get_logger().info('finished, returning result')

        # return to action client result response function
        return result
        
        
    def parameters_complete(self, goal_handle):
        # check if the parameters for the corresponding gesture are given
        match goal_handle.pib_gesture:
            case "look_at" | "locate_object":
                return goal_handle.has_input_vector
    
            case "point_to":
                return (
                    goal_handle.has_input_vector
                    and goal_handle.pib_side != "none"
                    and goal_handle.pib_mode != "none"
                    and goal_handle.pib_hand != "none"
                )
                
            case "offer_hand":
                return (
                    goal_handle.pib_side != "none"
                    and goal_handle.pib_mode != "none"
                )

            case "open_hand" | "close_hand":
                return goal_handle.pib_side != "none"

            case "greet_person":
                return (
                    goal_handle.has_input_vector
                    and goal_handle.pib_side != "none"
                    and goal_handle.pib_mode != "none"
                )

            case "go_rest":
                return goal_handle.pib_mode != "none"
                
            #case "face_follow":
            #    return True

            case _:
                return False
                
    def create_object_vector(self, vector):
        return Object_Vector.create_object_vector(
            "object_vector",
            (vector.x, vector.y, vector.z)
        )
            
    
    gesture_functions = {
        "look_at": lambda p: look_at(
            p["object_vector"]
        ),

        "point_to": lambda p: point_to(
            p["object_vector"],
            p["pib_side"],
            p["pib_mode"],
            p["pib_hand"]
        ),

        "offer_hand": lambda p: offer_hand(
            p["pib_side"],
            p["pib_mode"]
        ),

        "open_hand": lambda p: open_hand(
            p["pib_side"]
        ),

        "close_hand": lambda p: close_hand(
            p["pib_side"]
        ),

        "greet_person": lambda p: greet_person(
            p["object_vector"],
            p["pib_side"],
            p["pib_mode"]
        ),

        "locate_object": lambda p: locate_object(
            p["object_vector"]
        ),

        "go_rest": lambda p: go_rest(
            p["pib_mode"]
        )

        #"face_follow": lambda p: face_follow()
    }


# entry point for action server
def main(args = None):
    rclpy.init(args = args)

    # action server construction
    pib_gestures_server = PibGesturesServer()

    # self.get_logger().info('server created, starting server')
    
    # run action client until rclpy.shutdown()
    rclpy.spin(pib_gestures_server)

    # shut down the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    # pib_gestures_server.destroy_node()
    # rclpy.shutdown()

    # self.get_logger().info('server shut down')

if __name__ == '__main__':
    main()
