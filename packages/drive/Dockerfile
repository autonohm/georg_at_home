FROM georg-ros:humble

SHELL ["/bin/bash", "-c"]

WORKDIR /ws


# todo make this work over rosdep
# Q: is there a way to add rosdep dependencies without a ros package
RUN apt-get update && apt-get install --no-install-recommends -y \
    ros-humble-joy-linux \
    ros-humble-tf2 \
    ros-humble-tf2-ros \
    ros-humble-tf2-geometry-msgs \
    ros-humble-tf2-sensor-msgs

# change this variable to trick docker cache into rebuilding
ENV REBUILD=1

# clone directly into ws folder
RUN git clone https://github.com/EduArt-Robotik/edu_robot.git --branch hotfix/single_channel_motor_controller && \
    git clone https://github.com/EduArt-Robotik/edu_robot_control.git && \
    git clone https://github.com/snaens/twist_smoother.git

#COPY ./ros_packages/georg_interfaces ros2_ws/georg_interfaces
# COPY . ros2_ws/drive

RUN rosdep install --from-paths . --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

RUN /bin/bash -c "\
    source /opt/ros/humble/setup.bash && \
    colcon build --symlink-install \
    "

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
