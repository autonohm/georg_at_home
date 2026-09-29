FROM georg-ros:jazzy

SHELL ["/bin/bash", "-c"]

WORKDIR /ws

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
        btop \
        qt5ct \
        fonts-comfortaa \
        ros-jazzy-joy-linux \
        ros-jazzy-rviz2 \
        ros-jazzy-rqt \
        ros-jazzy-zbar-ros \
        ros-jazzy-rqt-robot-monitor \
        ros-jazzy-rqt-reconfigure \
        ros-jazzy-rqt-tf-tree \
        ros-jazzy-rqt-image-view \
        ros-jazzy-image-transport-plugins

# change this variable to trick docker cache into rebuilding
ENV REBUILD=1

# clone directly into ws folder
RUN git clone https://github.com/snaens/georg_description.git

RUN rosdep install --from-paths . --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

RUN /bin/bash -c "\
    source /ws/install/setup.bash && \
    colcon build --symlink-install \
    "

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
