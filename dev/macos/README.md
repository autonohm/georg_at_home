# ROS 2 Jazzy on macOS (Apple Silicon)

Development without Docker: ROS 2 Jazzy from [RoboStack](https://robostack.github.io/) via [pixi](https://pixi.sh).
The robot and the official build use the Docker images. This is only for working on a Mac.

## Setup (once)

```bash
# pixi as native arm64 binary (Homebrew on this Mac is the Intel version)
mkdir -p ~/.pixi/bin
curl -sSL https://github.com/prefix-dev/pixi/releases/latest/download/pixi-aarch64-apple-darwin.tar.gz | tar xz -C ~/.pixi/bin

cd dev/macos
# the repo path contains a space; ROS setup scripts and make break on that,
# so the environment lives outside the repo
~/.pixi/bin/pixi config set --local detached-environments "$HOME/.pixi-envs"
~/.pixi/bin/pixi install            # ROS 2 Jazzy, about 2 GB
~/.pixi/bin/pixi install -e ui      # Burr UI, small
```

## Daily use (from `dev/macos`)

| Command | What it does |
| --- | --- |
| `pixi run build` | colcon build of every package in `packages/` into `~/.cache/georg-ros-ws` |
| `pixi run test` | pytest for the task manager (Burr, validator) and the command gate |
| `pixi run test_ros` | P2 integration: task manager + mock packages over ROS, all mandatory scenarios (~1 min) |
| `pixi run task_manager` | task manager node in namespace `/georg` (Idle, start missions via services) |
| `GEORG_MOCK_SCENARIO=all_ok pixi run mock_packages` | mock packages for manual tests |
| `pixi run demo` | Burr demo with fake tasks, three runs |
| `pixi run -e ui burr_ui` | Burr UI on <http://localhost:7241> |
| `pixi run ros` | interactive shell with ROS and the workspace loaded |

## Known limits

- **macOS strips `DYLD_LIBRARY_PATH` when `bash` starts (SIP).** The tasks above re-source the workspace, so use them instead of plain `pixi run bash`.
- **Not available:** the audio package's TensorFlow / faster-whisper dependencies and the drive driver (`edu_robot`). Neither is needed for the task manager.
- **DDS discovery is limited to localhost** (`ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST`), so nothing on the Mac talks to the robot network.
- **The ROS pytest plugins do not match the installed pytest;** `pixi run test` switches plugin autoload off.
