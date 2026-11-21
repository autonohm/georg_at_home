FROM georg-ros:jazzy

SHELL ["/bin/bash", "-c"]

WORKDIR /ws

# change this variable to trick docker cache into rebuilding
ENV REBUILD=1

# georg_speech_msgs and pib-backend's datatypes come from the base image
COPY ./pib_bridge_pkg /ws/pib_bridge_pkg

RUN apt-get update && \
    rosdep install --from-paths . --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

RUN source /ws/install/setup.bash && colcon build --packages-select pib_bridge

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
