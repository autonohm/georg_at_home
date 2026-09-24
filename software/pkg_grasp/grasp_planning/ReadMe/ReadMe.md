## ROS2 action for grasp planning

'grasp_planning' is a ROS2 action consisting of the 'grasp_planning_server' and the grasp_planning_client'. 


### Prerequisites

In order to use this action, the D(R, O) Grasp Model has to be installed and trained.

### Structure

The 'grasp_planning_client' contains the path to D(R, O)s validate.py script. This has to be modified if run on a new computer for the first time! More changes in this file can include the name of the hand(s), the decision of left or right hand or the reach of the robot. 

The 'grasp:planning_server' handles the call of the validate.py script using an interactive terminal and sourcing miniconda beforehand. Due to that, the path to miniconda and to the D(R, O) Grasp Model have to be modified upon first use.

(Conda and ROS2 can't live inside the same terminal by default due to interference problems)


### Usage

To build this specific action use the following line: 'colcon build --packages-select grasp_planning grasp_planning'
To run this two terminals windows are nesseccary, one for the start of the server via 'ros2 run grasp_planning grasp_planning_server.py' and the other for the client using 'ros2 run grasp_planning grasp_planning_client.py'. 

If run with a statemachine nothing else should be neccessary. For debugging or testing of the action a separate node 'input_grasp_planning' is provided. Instructions for the latter are included with the node. 

All three nodes have to be running at the same time, the 'grasp_planning_client' is waiting for input via the object information topics. When all three topics are provided the client checks the information and triggers the server, which in turn starts the validate.py. Since the validate.py visualizes it's results a temporary window appears, usually accompanied with a message that something isn't responding. This message can be ignored as Isaac Gym, which is used for visualization by the grasp model, takes a moment to load.
