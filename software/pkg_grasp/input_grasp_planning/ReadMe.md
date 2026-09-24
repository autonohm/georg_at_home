## Read Me for input_grasp_planning
This node is for _testing or debugging_ the 'grasp_planning' action _without_ the use of a _statemachine_. 

## Usage:
To build this specific node run 'colcon build --packages-select input_grasp_planning input_grasp_planning'
To run this node use 'ros2 run input_grasp_planning publisher_node'

The Terminal this node is run in then asks you to enter the object_name and object_coordinates, which are entered via keyboard. The coordinates should be given in meters relative to a fictive sensor in the middle of pibs chest (See the file of all of pibs coordinate systems).
From the input the distance to the object is calculated. Name, coordinates and distance are then published on separate topics. 
This node doesn't have a build in stop and always reruns the input form once completed.