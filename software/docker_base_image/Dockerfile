FROM ros:jazzy

WORKDIR /ws

RUN apt-get update && apt-get install --no-install-recommends -y \
    ros-${ROS_DISTRO}-diagnostics

# clone directly into ws folder, src folder is optional
RUN git clone https://github.com/autonohm/georg_interfaces

RUN rosdep install --from-paths . --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

RUN /bin/bash -c "\
    source /opt/ros/${ROS_DISTRO}/setup.bash && \
    colcon build --symlink-install \
    "

RUN sed -i '/source/a source "/ws/install/setup.bash" --' /ros_entrypoint.sh
RUN echo "source /ws/install/setup.bash" >> /root/.bashrc

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
