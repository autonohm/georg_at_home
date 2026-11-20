FROM georg-ros:jazzy

SHELL ["/bin/bash", "-c"]

WORKDIR /ws

# MuJoCo (stage 2) from pip; stage 1 (sim2d) needs nothing extra
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip \
    && rm -rf /var/lib/apt/lists/* \
    && python3 -m pip install --no-cache-dir --break-system-packages mujoco==3.3.7

# change this variable to trick docker cache into rebuilding
ENV REBUILD=1

COPY ./georg_sim /ws/georg_sim

RUN apt-get update && \
    rosdep install --from-paths . --ignore-src -r -y && \
    rm -rf /var/lib/apt/lists/*

RUN /bin/bash -c "\
    source /ws/install/setup.bash && \
    colcon build --symlink-install \
    "

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
