FROM ros:humble-ros-core

SHELL ["/bin/bash", "-c"]

WORKDIR /app

RUN apt-get update && apt-get install --no-install-recommends -y \
        build-essential \
    && rm -rf /var/lib/apt/lists/*


# # COPY ./ros_packages/motors/pib_motors ./motors/pib_motors
# COPY ./ros_packages/examples ./motors/pib_motors
# RUN pip install ./motors/pib_motors

COPY ./ros_packages/georg_interfaces ros2_ws/georg_interfaces
COPY ./ros_packages/examples ros2_ws/examples

RUN cd ros2_ws && \
    source /opt/ros/humble/setup.bash && \
    colcon build

COPY ./ros_packages/ros_entrypoint.sh /

RUN chmod +x /ros_entrypoint.sh

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
