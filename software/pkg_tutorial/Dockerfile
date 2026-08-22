FROM georg-ros:humble

WORKDIR /ws


RUN apt-get update && apt-get install --no-install-recommends -y \
    ros-humble-examples-rclcpp-minimal-subscriber \
    ros-humble-examples-rclcpp-minimal-publisher

# copy directly into ws folder, src folder is optional
COPY py_pubsub/ src/py_pubsub/

RUN rosdep install --from-paths . --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

RUN /bin/bash -c "\
    source /opt/ros/humble/setup.bash && \
    colcon build --symlink-install \
    "


ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]

