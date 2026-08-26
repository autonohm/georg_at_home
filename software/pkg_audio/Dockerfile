FROM georg-ros:humble

SHELL ["/bin/bash", "-c"]
WORKDIR /ws

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        build-essential \
        curl \
        python3-colcon-common-extensions \
        python3-colcon-mixin \
        python3-pip \
        pulseaudio \
        portaudio19-dev \
        libusb-1.0-0-dev \
        libsndfile1 \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY audio_datatypes/ audio_datatypes/
COPY audio/ audio/

RUN /bin/bash -c "\
    source /opt/ros/humble/setup.bash && \
    colcon build \
    "

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

RUN pip install --no-cache-dir \
    requests \
    pyaudio \
    google-genai \
    numpy \
    scipy \
    tensorflow \
    tensorflow-hub

ENV PYTHONUNBUFFERED=1
ENV PULSE_SERVER=unix:"${XDG_RUNTIME_DIR}/pulse/native"

ENTRYPOINT ["/ros_entrypoint.sh"]

CMD ["bash"]
