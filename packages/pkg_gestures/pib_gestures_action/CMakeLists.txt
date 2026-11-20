cmake_minimum_required(VERSION 3.10)
project(pib_gestures_action)

find_package(ament_cmake REQUIRED)

# Action definition lives in pkg_interfaces/georg_gesture_msgs

install(
  PROGRAMS
    modules/pib_gestures_client.py
    modules/pib_gestures_server.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
