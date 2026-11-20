FROM georg-ros:jazzy

SHELL ["/bin/bash", "-c"]

WORKDIR /ws

# change this variable to trick docker cache into rebuilding
ENV REBUILD=1

COPY ./command_gate /ws/command_gate

RUN apt-get update && \
    rosdep install --from-paths . --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

RUN /bin/bash -c "\
    source /ws/install/setup.bash && \
    colcon build --symlink-install \
    "

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
