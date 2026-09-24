cmake_minimum_required(VERSION 3.8)
project(grasp_planning)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

find_package(geometry_msgs REQUIRED)

ament_python_install_package(modules)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/GraspPlanning.action"
  DEPENDENCIES geometry_msgs std_msgs
)

install(PROGRAMS
  modules/grasp_planning_client.py
  modules/grasp_planning_server.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_export_dependencies(rosidl_default_runtime)

ament_package()
