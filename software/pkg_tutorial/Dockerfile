FROM georg-ros:humble

WORKDIR /ws


RUN apt-get update && apt-get install --no-install-recommends -y \
    ros-humble-examples-rclcpp-minimal-subscriber \
    ros-humble-examples-rclcpp-minimal-publisher \
    && rm -rf /var/lib/apt/lists/*


ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
