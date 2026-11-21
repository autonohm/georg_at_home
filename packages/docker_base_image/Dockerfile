FROM ros:jazzy

WORKDIR /ws

RUN apt-get update && apt-get install --no-install-recommends -y \
    ros-${ROS_DISTRO}-diagnostics

# clone directly into ws folder, src folder is optional
RUN git clone https://github.com/autonohm/georg_interfaces

# shared interfaces of this repo (packages/pkg_interfaces), passed in as build context "interfaces"
COPY --from=interfaces . /ws/pkg_interfaces

# message package of pib-backend (PlayAudioFromSpeech, ApplyJointTrajectory, ...), so Georg's
# containers can talk to pib-backend. Pinned to the pib-backend release running on the Jetson
# (v0.7.10); update together with pib-backend.
ARG PIB_BACKEND_REF=f3a8a3762ae7710f9001c74cebad683d5719f6df
RUN git clone https://github.com/pib-rocks/pib-backend /tmp/pib-backend \
    && git -C /tmp/pib-backend checkout ${PIB_BACKEND_REF} \
    && cp -r /tmp/pib-backend/ros_packages/datatypes /ws/datatypes \
    && rm -rf /tmp/pib-backend

# apt-get update again: the update above may come from an old build cache (404 on packages.ros.org)
RUN apt-get update && \
    rosdep install --from-paths . --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

RUN /bin/bash -c "\
    source /opt/ros/${ROS_DISTRO}/setup.bash && \
    colcon build --symlink-install \
    "

RUN sed -i '/source/a source "/ws/install/setup.bash" --' /ros_entrypoint.sh
RUN echo "source /ws/install/setup.bash" >> /root/.bashrc

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
