"""Mock packages (P2): fake action servers for every package the task manager calls.

Same action names and types as the real packages, so the task manager cannot
tell the difference. What each server answers is set by a scenario (YAML)::

    # mocks/scenarios/one_fails.yaml
    gesture: {result: fail, after_s: 0.3}
    listen:  {result: success, after_s: 0.3}

Keys are catalog task names (``listen``, ``gesture``, ``navigate_object``, ...)
or action names (``nav/drive_route``). Action names win. A value is one
behaviour or a list of behaviours used one after another (the last one repeats):

    result:  success | fail | timeout | unreachable
    after_s: seconds until the answer (default 0.3)

``timeout`` never answers, the task's own timeout or a cancel ends it.
``unreachable`` does not create the server at all.
Cancel is always honoured within 0.1 s (plan: abort within 2 s).

Also publishes ``odom`` (robot at 0/0), because navigation tasks need a position.
Set ``odom: false`` in the scenario when a simulator or the robot provides odom.

    ros2 run task_manager mock_packages --scenario all_ok
"""

import argparse
import os
import threading
import time

from datatypes.action import Listen
from geometry_msgs.msg import Point
from georg_gesture_msgs.action import PibGesturesInterface
from georg_nav_msgs.action import DriveRoute, Navigate
from nav_msgs.msg import Odometry
import rclpy
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from task_manager.catalog import load_catalog
import yaml

SCENARIO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scenarios')
DEFAULT = {'result': 'success', 'after_s': 0.3}

ACTION_TYPES = {
    'datatypes/action/Listen': Listen,
    'georg_gesture_msgs/action/PibGesturesInterface': PibGesturesInterface,
    'georg_nav_msgs/action/Navigate': Navigate,
}
EXTRA_ACTION_TYPES = {'nav/drive_route': DriveRoute}


def load_scenario(name_or_path: str) -> dict:
    path = name_or_path
    if not os.path.exists(path):
        path = os.path.join(SCENARIO_DIR, f'{name_or_path}.yaml')
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def _result(action_type, ok: bool):
    """Build the result message of a finished goal, success or failure."""
    if action_type is Listen:
        r = Listen.Result()
        r.detected, r.confidence, r.transcript = ok, 0.9 if ok else 0.1, 'mock' if ok else ''
    elif action_type is PibGesturesInterface:
        r = PibGesturesInterface.Result()
        r.success, r.message = (0, 'mock ok') if ok else (1, 'mock failure')
    elif action_type is Navigate:
        r = Navigate.Result()
        r.result_code = Navigate.Result.RESULT_OK if ok else Navigate.Result.RESULT_NO_PATH_FOUND
        r.waypoints = [Point(x=1.0, y=0.0, z=0.0)] if ok else []
        r.path_length_m = 1.0 if ok else 0.0
    else:
        r = DriveRoute.Result()
        r.result_code = DriveRoute.Result.RESULT_OK if ok \
            else DriveRoute.Result.RESULT_OBSTACLE_DETECTED
    return r


class MockPackages(Node):

    def __init__(self, scenario: dict):
        super().__init__('mock_packages')
        self._scenario = scenario
        self._calls = {}
        self._lock = threading.Lock()
        self._cb = ReentrantCallbackGroup()
        self._servers = []

        for action, (action_type, task) in self._actions().items():
            first = self._behaviours(action, task)[0]
            if first.get('result') == 'unreachable':
                self.get_logger().info(f'{action}: unreachable (no server)')
                continue
            self._servers.append(ActionServer(
                self, action_type, action,
                execute_callback=lambda goal, a=action, t=task, at=action_type:
                    self._execute(goal, a, t, at),
                goal_callback=lambda _goal: GoalResponse.ACCEPT,
                cancel_callback=lambda _goal: CancelResponse.ACCEPT,
                callback_group=self._cb))
            self.get_logger().info(f'{action}: {first}')

        if scenario.get('odom', True):
            self._odom = self.create_publisher(Odometry, 'odom', 10)
            self.create_timer(0.1, self._publish_odom)
        else:
            self.get_logger().info('odom: off (provided by simulator or robot)')

    def _actions(self):
        """Map each action name to (type, catalog task name), from the catalog."""
        out = {}
        for name, spec in load_catalog().tasks.items():
            if spec.action and spec.type in ACTION_TYPES:
                out.setdefault(spec.action, (ACTION_TYPES[spec.type], name))
            for extra in spec.extra_actions:
                if extra in EXTRA_ACTION_TYPES:
                    out.setdefault(extra, (EXTRA_ACTION_TYPES[extra], name))
        return out

    def _behaviours(self, action: str, task: str):
        value = self._scenario.get(action, self._scenario.get(task, DEFAULT))
        items = value if isinstance(value, list) else [value]
        return [dict(DEFAULT, **(item or {})) for item in items]

    def _next_behaviour(self, action: str, task: str) -> dict:
        items = self._behaviours(action, task)
        with self._lock:
            n = self._calls.get(action, 0)
            self._calls[action] = n + 1
        return items[min(n, len(items) - 1)]

    def _execute(self, goal_handle, action, task, action_type):
        behaviour = self._next_behaviour(action, task)
        result, after = behaviour['result'], float(behaviour['after_s'])
        self.get_logger().info(f'{action}: goal received -> {result} after {after}s')
        start = time.monotonic()
        while result == 'timeout' or time.monotonic() - start < after:
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                self.get_logger().info(f'{action}: canceled')
                return _result(action_type, ok=False)
            if not rclpy.ok():
                break
            time.sleep(0.05)
        ok = result == 'success'
        if ok:
            goal_handle.succeed()
        else:
            goal_handle.abort()
        self.get_logger().info(f"{action}: {'succeeded' if ok else 'failed'}")
        return _result(action_type, ok)

    def _publish_odom(self):
        msg = Odometry()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'odom'
        msg.pose.pose.orientation.w = 1.0
        self._odom.publish(msg)


def main(args=None):
    parser = argparse.ArgumentParser(description='Mock packages for the task manager')
    parser.add_argument('--scenario', default=os.environ.get('GEORG_MOCK_SCENARIO', 'all_ok'),
                        help='name in mocks/scenarios/ or path to a YAML file')
    known, ros_args = parser.parse_known_args(args)
    rclpy.init(args=ros_args)
    node = MockPackages(load_scenario(known.scenario))
    node.get_logger().info(f"mock packages ready, scenario '{known.scenario}'")
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
