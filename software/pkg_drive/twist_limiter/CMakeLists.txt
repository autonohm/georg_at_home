cmake_minimum_required(VERSION 3.10)
project(twist_limiter)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_components REQUIRED)
find_package(geometry_msgs REQUIRED)

add_executable(twist_limiter_node src/main.cpp)
ament_target_dependencies(twist_limiter_node
                          geometry_msgs
                          rclcpp)

add_executable(dynamic_signal_generator src/dynamic_signal_generator.cpp)
ament_target_dependencies(dynamic_signal_generator
                          geometry_msgs
                          rclcpp)

install(TARGETS
    twist_limiter_node
    dynamic_signal_generator
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
