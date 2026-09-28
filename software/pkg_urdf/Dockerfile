FROM georg-ros:jazzy

SHELL ["/bin/bash", "-c"]

WORKDIR /ws

RUN apt-get update && apt-get install --no-install-recommends -y \
    ros-jazzy-xacro \
    ros-jazzy-robot-state-publisher \
    ros-jazzy-joint-state-publisher \
    && rm -rf /var/lib/apt/lists/*

# change this variable to trick docker cache into rebuilding
ENV REBUILD=1

RUN git clone https://github.com/snaens/georg_description.git

RUN /bin/bash -c "\
    source /ws/install/setup.bash && \
    colcon build --symlink-install \
    "

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
