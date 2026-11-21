FROM georg-ros:jazzy

SHELL ["/bin/bash", "-c"]

WORKDIR /ws

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# pib-sdk is NOT installed: all pib_sdk imports in pib_gestures are commented out, and the
# SDK drives the pib servos via rosbridge past the command_gate (hardware scan P7).
# On arm64, pib-sdk 0.9.1 -> pin -> cmeel-boost also needs numpy>=2.2, which conflicts with
# the system numpy 1.26.4 of ROS Jazzy. numpy itself comes with the base image.
# Before re-enabling: route servo commands through ROS topics behind a gate, then e.g.
#   RUN python3 -m pip install --no-cache-dir --break-system-packages pib-sdk==0.9.1

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
