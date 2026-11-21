FROM georg-ros:jazzy

SHELL ["/bin/bash", "-c"]

WORKDIR /ws

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip \
    python3-dev \
    build-essential \
    git \
    ros-jazzy-rosbag2 \
    ros-jazzy-rosbag2-storage-mcap \
    && rm -rf /var/lib/apt/lists/*

# Burr (P1) in its own venv. --system-site-packages keeps rclpy from Jazzy visible,
# PYTHONPATH makes the venv visible to `ros2 run` scripts (they use /usr/bin/python3).
RUN apt-get update && apt-get install -y --no-install-recommends python3-venv \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m venv --system-site-packages /opt/burr-venv \
    && /opt/burr-venv/bin/pip install --no-cache-dir "apache-burr[tracking]==0.43.0"
ENV PYTHONPATH=/opt/burr-venv/lib/python3.12/site-packages
ENV GEORG_BURR_STORAGE_DIR=/root/.burr

# change this variable to trick docker cache into rebuilding
ENV REBUILD=1

# Interfaces (georg_nav_msgs, georg_gesture_msgs, georg_task_manager_msgs, georg_speech_msgs, pib-backend datatypes)
# come from the base image (packages/pkg_interfaces).
COPY ./task_manager_pkg /ws/task_manager
# NavigateObject/NavigateRoom import navigate_server.grid_rasterizer directly.
# Until that is resolved in P1 (docs/OPEN_ISSUES.md T3) the package is built here too.
COPY --from=navigation ./navigate_server_pkg /ws/navigate_server_pkg
# Maps are mounted from packages/pkg_slam/maps at runtime (docker-compose.yaml).

#RUN git clone https://github.com/Giusaurus/pkg_navigation.git

RUN rosdep install --from-paths . --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

RUN /bin/bash -c "\
    source /ws/install/setup.bash && \
    colcon build --symlink-install \
    "

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
