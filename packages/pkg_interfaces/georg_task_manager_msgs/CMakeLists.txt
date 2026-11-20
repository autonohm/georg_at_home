cmake_minimum_required(VERSION 3.8)
project(georg_task_manager_msgs)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(builtin_interfaces REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/MissionStatus.msg"
  "srv/StartMission.srv"
  "srv/CancelMission.srv"
  "srv/ListMissions.srv"
  "srv/SetMode.srv"
  "srv/Instruct.srv"
  "srv/ApprovePlan.srv"
  DEPENDENCIES builtin_interfaces
)

ament_export_dependencies(rosidl_default_runtime)

ament_package()
