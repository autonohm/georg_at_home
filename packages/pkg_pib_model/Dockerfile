FROM georg-ros:jazzy

SHELL ["/bin/bash", "-c"]

WORKDIR /ws

RUN apt-get update && apt-get install -y --no-install-recommends \
    ros-jazzy-robot-state-publisher curl unzip \
    && rm -rf /var/lib/apt/lists/*

# pib web model (the one Cerebra shows) from the pib-3d release, same pin as pib-backend
# (robot_model_version.txt). Not in this repo: license of pib-3d unclear (repo AGPL-3.0,
# package.xml "Proprietary"), and a new model version only needs a new pin.
ARG PIB_MODEL_VERSION=v0.11.6
ARG PIB_MODEL_SHA256=7954575a4bca8942a074abfebd9744e0ead5e6e20bf99a310e82b50c680cc251

# change this variable to trick docker cache into rebuilding
ENV REBUILD=1

COPY ./pib_model_pkg /ws/pib_model_pkg
RUN curl -sSL --fail -o /tmp/model.zip \
      "https://github.com/pib-rocks/pib-3d/releases/download/${PIB_MODEL_VERSION}/robot-model-${PIB_MODEL_VERSION}.zip" \
    && echo "${PIB_MODEL_SHA256}  /tmp/model.zip" | sha256sum -c - \
    && mkdir -p /tmp/model && unzip -q /tmp/model.zip -d /tmp/model \
    && cd /ws/pib_model_pkg && python3 -m pib_model.convert /tmp/model model \
    && rm -rf /tmp/model /tmp/model.zip

# no --symlink-install: the bridge image copies the installed package
RUN source /ws/install/setup.bash && colcon build --packages-select pib_model

ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
