#!/usr/bin/env python3

import rclpy

from std_msgs.msg import String
from geometry_msgs.msg import Vector3

from rclpy.action import ActionServer, GoalResponse
from rclpy.node import Node

from pib_gestures_action.action import PibGesturesInterface # interface with data types

# import your core function here
from pib_gestures.src.pib_gestures.core import look_at, point_to, greet_person

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
    def goal_callback(self, goal_request):
        self.goal = goal_request

    	# validating goal content is in accepted range
        if not self.goal.gesture:
            return GoalResponse.REJECT
            
        # if only accepting one goal at a time
        if self._goal_running:
            return GoalResponse.REJECT
        else:
            return GoalResponse.ACCEPT


    # execution function
    # executed after acccepting goal
    def execute_callback(self, goal_handle):
        self.get_logger().info('starting execution')
        
        # starting execution
        self.goal_running = True
        
        # result data types from action/PibGesturesInterface.action
        result = PibGesturesInterface.Result()

        try:
            if self.goal.gesture == "look_at":
                # here starts the execution of the core functionality
                result.success = look_at(
                    self.goal.camera_vector.x,
                    self.goal.camera_vector.y,
                    self.goal.camera_vector.z
                )
                
            elif self.goal.gesture == "point_to":
                # here starts the execution of the core functionality
                result.success = point_to(
                    self.goal.camera_vector.x,
                    self.goal.camera_vector.y,
                    self.goal.camera_vector.z,
                    self.goal.pib_side,
                    self.goal.pib_gesture,
                    self.goal.pib_hand
                )
                
            elif self.goal.gesture == "greet_person":
                # here starts the execution of the core functionality
                result.success = greet_person(
                    self.goal.camera_vector.x,
                    self.goal.camera_vector.y,
                    self.goal.camera_vector.z,
                    self.goal.pib_side,
                    self.goal.pib_gesture
                )

            else:
                raise Exception('faulty gesture selection')

            # successful execution
            goal_handle.succeed()
            result.success = 0
            result.message = 'executed successfully'

                
        # error in execution of my_function
        except Exception as error_message:     
            result.success = -1
            result.message = error_message
            goal_handle.abort()

        # client canceling execution
        if goal_handle.is_cancel_requested:
            result.success = 1
            result.message = 'client canceled request'            
            goal_handle.canceled()

        # finished execution
        self._goal_running = False

        # return to action client result response function
        return result


# entry point for action server
def main(args = None):
    rclpy.init(args = args)

    # action server construction
    pib_gestures_server = PibGesturesServer()
    
    # run action client until rclpy.shutdown()
    rclpy.spin(pib_gestures_server)

    # shut down the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    # topic_template_subscriber.destroy_node()
    # rclpy.shutdown()

if __name__ == '__main__':
    main()
