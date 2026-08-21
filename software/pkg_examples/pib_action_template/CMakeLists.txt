cmake_minimum_required(VERSION 3.8)
project(pib_action_template)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

ament_python_install_package(modules)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/Template.action"
)

install(PROGRAMS
  modules/action_template_client.py
  modules/action_template_server.py
  modules/action_demo_client.py
  modules/action_demo_server.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_export_dependencies(rosidl_default_runtime)

ament_package()
