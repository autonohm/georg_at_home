FROM georg-ros:jazzy

SHELL ["/bin/bash", "-c"]

WORKDIR /ws


# todo make this work over rosdep
# Q: is there a way to add rosdep dependencies without a ros package
RUN apt-get update && apt-get install --no-install-recommends -y \
    ros-jazzy-joy-linux \
    ros-jazzy-diagnostic-updater \
    ros-jazzy-tf2 \
    ros-jazzy-tf2-ros \
    ros-jazzy-tf2-geometry-msgs \
    ros-jazzy-tf2-sensor-msgs

# change this variable to trick docker cache into rebuilding
ENV REBUILD=1

# clone directly into ws folder
RUN git clone https://github.com/EduArt-Robotik/edu_robot.git --branch hotfix/single_channel_motor_controller && \
    git clone https://github.com/EduArt-Robotik/edu_robot_control.git

COPY twist_limiter/ twist_limiter/

RUN rosdep install --from-paths . --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

RUN /bin/bash -c "\
    source /ws/install/setup.bash && \
    colcon build --symlink-install \
    "

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
