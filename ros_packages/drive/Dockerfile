FROM ros:humble-ros-core

SHELL ["/bin/bash", "-c"]

WORKDIR /app


# todo make this work over rosdep
# Q: is there a way to add rosdep dependencies without a ros package
RUN apt-get update && apt-get install --no-install-recommends -y \
        ros-humble-diagnostics \
        ros-humble-hardware-interface \
        ros-humble-pluginlib \
        ros-humble-joy-linux \
        ros-humble-tf2 \
        ros-humble-tf2-ros \
        ros-humble-tf2-geometry-msgs \
        ros-humble-tf2-sensor-msgs \
        # ros-humble-vision-msgs \
        git python3-colcon-common-extensions \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

ENV REBUILD=2

RUN git clone https://github.com/EduArt-Robotik/edu_robot.git --branch hotfix/single_channel_motor_controller ros2_ws/edu_robot && \
    git clone https://github.com/EduArt-Robotik/edu_robot_control.git ros2_ws/edu_robot_control

#COPY ./ros_packages/georg_interfaces ros2_ws/georg_interfaces
COPY ./ros_packages/drive ros2_ws/drive

RUN cd ros2_ws && \
    source /opt/ros/humble/setup.bash && \
    colcon build

COPY ./ros_packages/ros_entrypoint.sh /

RUN chmod +x /ros_entrypoint.sh

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
