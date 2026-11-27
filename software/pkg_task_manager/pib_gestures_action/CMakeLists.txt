cmake_minimum_required(VERSION 3.10)
project(pib_gestures_action)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

find_package(rosidl_default_generators REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(std_msgs REQUIRED)

# Generate action interface
rosidl_generate_interfaces(${PROJECT_NAME}
  "action/PibGesturesInterface.action"
  DEPENDENCIES
    geometry_msgs
    std_msgs
)

# Install Python packages
ament_python_install_package(pib_gestures
  PACKAGE_DIR modules/pib_gestures/src/pib_gestures
)

# Install executable ROS nodes
install(PROGRAMS
  modules/pib_gestures_client.py
  modules/pib_gestures_server.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_export_dependencies(rosidl_default_runtime)

ament_package()

