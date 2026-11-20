FROM georg-ros:jazzy

SHELL ["/bin/bash", "-c"]

WORKDIR /ws

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# pib-sdk replaces the former broken git submodule modules/pib_sdk.
# Note: all pib_sdk imports in pib_gestures are commented out at the moment.
RUN python3 -m pip install --no-cache-dir --break-system-packages \
    numpy==1.26.4 \
    pib-sdk==0.9.1

# change this variable to trick docker cache into rebuilding
ENV REBUILD=1

# georg_gesture_msgs comes from the base image (packages/pkg_interfaces)
COPY ./pib_gestures_action /ws/pib_gestures_action

RUN apt-get update && \
    rosdep install --from-paths . --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

RUN /bin/bash -c "\
    source /ws/install/setup.bash && \
    colcon build --symlink-install \
    "

RUN chmod +x /ws/install/pib_gestures_action/lib/pib_gestures_action/pib_gestures_*

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
