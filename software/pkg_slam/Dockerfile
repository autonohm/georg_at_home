FROM georg-ros:humble

SHELL ["/bin/bash", "-c"]

WORKDIR /ws


# todo make this work over rosdep
# Q: is there a way to add rosdep dependencies without a ros package
RUN apt-get update && apt-get install --no-install-recommends -y \
    ros-humble-xacro \
    ros-humble-robot-state-publisher \
    ros-humble-slam-toolbox

# change this variable to trick docker cache into rebuilding
ENV REBUILD=1

# clone directly into ws folder
RUN git clone https://github.com/SICKAG/sick_scan_xd.git --branch 3.8.0 && \
    git clone https://github.com/MAPIRlab/rf2o_laser_odometry.git && \
    git clone https://github.com/BruceChanJianLe/laser_scan_merger.git

RUN rosdep install --from-paths . --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

RUN /bin/bash -c "\
    source /opt/ros/humble/setup.bash && \
    colcon build --symlink-install \
    "

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
