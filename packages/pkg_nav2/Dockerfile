FROM georg-ros:jazzy

SHELL ["/bin/bash", "-c"]

WORKDIR /ws

# change this variable to trick docker cache into rebuilding
ENV REBUILD=1

# Nav2 from the ROS apt repository (planner, MPPI controller, costmaps, behavior tree)
RUN apt-get update && apt-get install --no-install-recommends -y \
    ros-$ROS_DISTRO-navigation2 \
    ros-$ROS_DISTRO-nav2-bringup \
    && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
