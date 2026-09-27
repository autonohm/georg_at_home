FROM georg-ros:jazzy

SHELL ["/bin/bash", "-c"]

WORKDIR /ws

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-colcon-common-extensions \
    python3-rosdep \
    python3-pip \
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

# change this variable to trick docker cache into rebuilding
ENV REBUILD=1

COPY ./georg_task_manager /ws/georg_task_manager
COPY ./pib_gestures_action /ws/pib_gestures_action
COPY ./pib-audio /ws/pib-audio
COPY ./pkg_navigation /ws/pkg_navigation
COPY ./maps /root/georg_maps

#RUN git clone https://github.com/Giusaurus/pkg_navigation.git

RUN rosdep install --from-paths . --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

RUN /bin/bash -c "\
    source /opt/ros/jazzy/setup.bash && \
    colcon build --symlink-install \
    "

RUN chmod +x /ws/install/pib_gestures_action/lib/pib_gestures_action/pib_gestures_*

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
