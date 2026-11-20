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
    portaudio19-dev \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --no-cache-dir --break-system-packages \
    numpy==1.26.4 \
    tensorflow==2.16.2 \
    tensorflow-hub==0.16.1 \
    tf_keras==2.16.0 \
    PyAudio==0.2.14 \
    faster-whisper==1.2.1

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

# Interfaces (georg_nav_msgs, georg_gesture_msgs, georg_task_manager_msgs)
# come from the base image (packages/pkg_interfaces).
COPY ./georg_task_manager /ws/georg_task_manager
COPY ./pib-audio /ws/pib-audio
# NavigateObject/NavigateRoom import navigate_server.grid_rasterizer directly.
# Until that is resolved in P1 (OPEN_QUESTIONS Q4b) the package is built here too.
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
