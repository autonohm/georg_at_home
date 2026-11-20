FROM georg-ros:jazzy

SHELL ["/bin/bash", "-c"]

WORKDIR /ws

# change this variable to trick docker cache into rebuilding
ENV REBUILD=1

# georg_nav_msgs comes from the base image (packages/pkg_interfaces)
COPY ./navigate_server_pkg /ws/navigate_server_pkg
COPY ./drive_route_server_pkg /ws/drive_route_server_pkg

RUN apt-get update && \
    rosdep install --from-paths . --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

RUN /bin/bash -c "\
    source /ws/install/setup.bash && \
    colcon build --symlink-install \
    "

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
