FROM ros:jazzy

WORKDIR /ws

# change this variable to trick docker cache into rebuilding
ENV REBUILD=1

RUN apt-get update && apt-get install --no-install-recommends -y \
    ros-${ROS_DISTRO}-diagnostics

# clone directly into ws folder, src folder is optional
RUN git clone https://github.com/autonohm/georg_interfaces

# make pib-backend available
ARG PIB_BACKEND_REF=main
RUN git clone https://github.com/pib-rocks/pib-backend /tmp/pib-backend \
 && git -C /tmp/pib-backend checkout ${PIB_BACKEND_REF} \
 && cp -r /tmp/pib-backend/ros_packages/datatypes /ws/datatypes \
 && rm -rf /tmp/pib-backend

RUN rosdep install --from-paths . --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

RUN /bin/bash -c "\
    source /opt/ros/${ROS_DISTRO}/setup.bash && \
    colcon build --symlink-install \
    "

RUN sed -i '/source/a source "/ws/install/setup.bash" --' /ros_entrypoint.sh
RUN echo "source /ws/install/setup.bash" >> /root/.bashrc

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
