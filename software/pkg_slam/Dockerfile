FROM georg-ros:jazzy

SHELL ["/bin/bash", "-c"]

WORKDIR /ws


RUN apt-get update && apt-get install --no-install-recommends -y \
    ros-jazzy-slam-toolbox

# change this variable to trick docker cache into rebuilding
ENV REBUILD=1

# clone directly into ws folder
RUN git clone https://github.com/SICKAG/sick_scan_xd.git --branch 3.8.0 && \
    git clone https://github.com/MAPIRlab/rf2o_laser_odometry.git && \
    git clone https://github.com/BruceChanJianLe/laser_scan_merger.git

RUN rosdep install --from-paths . --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

RUN /bin/bash -c "\
    source /ws/install/setup.bash && \
    colcon build --symlink-install \
    "

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
