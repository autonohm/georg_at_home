"""Drive to a map position with Nav2 (pkg_nav2, action navigate_to_pose).

Used by NavigateObject and NavigateRoom. The place comes from the map YAML, Nav2 plans and
drives:

    place name -> (x, y) from the map YAML -> NavigateToPose (frame map) -> Nav2

The map YAML and the SLAM map share one frame in the simulation (SLAM starts at the sim_start
of the YAML). On the robot this needs a saved SLAM map with the places (OPEN_ISSUES S10).
"""

import asyncio
import math
import time

from action_msgs.msg import GoalStatus

from .timeout_watcher import as_asyncio_future

# pib looks this far left of the base x axis (FRONT_YAW_OFFSET of the former drive server)
FRONT_YAW_OFFSET_RAD = math.pi / 2
GOAL_RESPONSE_TIMEOUT_S = 10.0
GOAL_SEND_ATTEMPTS = 3


def facing_yaw(start, target) -> float:
    """Yaw at the goal so that pib faces the direction it came from start to target."""
    return math.atan2(target[1] - start[1], target[0] - start[0]) + FRONT_YAW_OFFSET_RAD


def make_goal(x: float, y: float, yaw: float):
    from nav2_msgs.action import NavigateToPose
    goal = NavigateToPose.Goal()
    goal.pose.header.frame_id = 'map'
    goal.pose.pose.position.x, goal.pose.pose.position.y = float(x), float(y)
    goal.pose.pose.orientation.z = math.sin(yaw / 2.0)
    goal.pose.pose.orientation.w = math.cos(yaw / 2.0)
    return goal


async def nav2_go(client, goal, timeout: float, abort_check=None, log=print) -> bool:
    """Send ``goal`` to Nav2 and wait. True only if Nav2 reports SUCCEEDED."""
    if not client.wait_for_server(timeout_sec=2.0):
        log('[TASK] nav2: navigate_to_pose not available (is pkg_nav2 running?)')
        return False
    handle = None
    for attempt in range(1, GOAL_SEND_ATTEMPTS + 1):
        # the goal response can get lost (DDS); a new goal replaces the old one in Nav2
        try:
            handle = await asyncio.wait_for(as_asyncio_future(client.send_goal_async(goal)),
                                            GOAL_RESPONSE_TIMEOUT_S)
            break
        except asyncio.TimeoutError:
            log(f'[TASK] nav2: no goal response (attempt {attempt}), sending again')
    if handle is None or not handle.accepted:
        log('[TASK] nav2: goal not accepted')
        return False

    result = as_asyncio_future(handle.get_result_async())
    start = time.time()
    while not result.done():
        if (abort_check is not None and abort_check()) or time.time() - start > timeout:
            await as_asyncio_future(handle.cancel_goal_async())
            log('[TASK] nav2: goal cancelled (abort or timeout)')
            return False
        await asyncio.sleep(0.1)
    response = result.result()
    if response.status == GoalStatus.STATUS_SUCCEEDED:
        return True
    r = response.result
    log(f'[TASK] nav2: status {response.status}, error {getattr(r, "error_code", "?")} '
        f'{getattr(r, "error_msg", "")}')
    return False
