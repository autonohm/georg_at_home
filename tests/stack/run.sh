#!/usr/bin/env bash
# Acceptance checks against the running stack: tests/stack/run.sh mock|sim
# Start the stack first: ./projectctl.bash up mock (or sim). Runs inside the task_manager
# container, so it uses the same ROS_DOMAIN_ID as the stack.
set -euo pipefail
profile=${1:-mock}
here=$(cd "$(dirname "$0")" && pwd)
container=georg-task_manager-1
if [[ "$profile" == "sim" ]]; then
    # fresh start pose: restart simulator and SLAM (the map would not fit a jumping robot)
    docker restart georg-sim-1 georg-slam-1 > /dev/null
    for _ in $(seq 1 30); do
        [[ "$(docker inspect -f '{{.State.Health.Status}}' georg-sim-1)" == healthy ]] && break
        sleep 2
    done
fi
docker cp "$here/stack_check.py" "$container:/tmp/stack_check.py"
docker exec "$container" bash -c "source /ws/install/setup.bash && python3 /tmp/stack_check.py $profile"
