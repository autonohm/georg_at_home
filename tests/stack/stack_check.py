"""Acceptance checks against the running compose stack (./projectctl.bash up mock|sim).

Runs inside the task_manager container, which has rclpy and the message packages:

    tests/stack/run.sh mock      # or: sim

Checks (plan P2/P3): missions can be listed and started, a mission ends with the expected
state, in sim the robot really reaches the seat with real navigation, SLAM publishes a map,
an abort stops the drive. Prints one line per check, exit code 1 if one fails.
"""
import math
import os
import sys
import threading
import time

from georg_task_manager_msgs.msg import MissionStatus
from georg_task_manager_msgs.srv import CancelMission, ListMissions, StartMission

from nav_msgs.msg import OccupancyGrid, Odometry

import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy

FINAL = {MissionStatus.SUCCEEDED, MissionStatus.FAILED, MissionStatus.ABORTED}
STATE = {0: 'IDLE', 1: 'RUNNING', 2: 'SUCCEEDED', 3: 'FAILED', 4: 'ABORTED'}
LATCHED = QoSProfile(depth=10, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                     reliability=ReliabilityPolicy.RELIABLE)


class Checker(Node):
    """Test node: service clients, mission status, odometry and map."""

    def __init__(self):
        """Create subscriptions and service clients."""
        super().__init__('stack_check')
        self.status = None
        self.statuses = []
        self.pose = None
        self.speed = None
        self.map = None
        self.create_subscription(MissionStatus, '/task_manager/status', self._on_status, LATCHED)
        self.create_subscription(Odometry, '/odom', self._on_odom, 10)
        self.create_subscription(OccupancyGrid, '/map', self._on_map,
                                 QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                                            reliability=ReliabilityPolicy.RELIABLE))
        self.start_cli = self.create_client(StartMission, '/task_manager/start')
        self.cancel_cli = self.create_client(CancelMission, '/task_manager/cancel')
        self.list_cli = self.create_client(ListMissions, '/task_manager/list_missions')

    def _on_status(self, msg):
        self.status = msg
        self.statuses.append(msg)

    def _on_odom(self, msg):
        p = msg.pose.pose.position
        t = msg.twist.twist
        self.pose = (p.x, p.y)
        self.speed = math.hypot(t.linear.x, t.linear.y) + abs(t.angular.z)

    def _on_map(self, msg):
        self.map = msg

    def call(self, cli, req, timeout=20.0):
        """Call a service and wait for the answer."""
        if not cli.wait_for_service(timeout_sec=timeout):
            raise RuntimeError(f'service {cli.srv_name} not available')
        fut = cli.call_async(req)
        end = time.time() + timeout
        while not fut.done() and time.time() < end:
            time.sleep(0.05)
        if not fut.done():
            raise RuntimeError(f'service {cli.srv_name}: no answer')
        return fut.result()

    def run_mission(self, mission_id, timeout=120.0, cancel_after=None):
        """Start a mission, optionally cancel it, and return its final status."""
        resp = self.call(self.start_cli, StartMission.Request(mission_id=mission_id))
        if not resp.accepted:
            raise RuntimeError(f'start {mission_id} rejected: {resp.reason}')
        app_id = resp.burr_app_id
        start = time.time()
        cancelled = False
        while time.time() - start < timeout:
            st = self.status
            if cancel_after is not None and not cancelled and time.time() - start > cancel_after:
                self.call(self.cancel_cli, CancelMission.Request())
                cancelled = True
            if st is not None and st.burr_app_id == app_id and st.state in FINAL:
                return st
            time.sleep(0.1)
        raise RuntimeError(f'{mission_id}: no final state after {timeout:.0f} s')


def wait_for(pred, timeout):
    """Wait until pred() is true."""
    end = time.time() + timeout
    while time.time() < end:
        if pred():
            return True
        time.sleep(0.1)
    return False


def seat_position(name='Seat'):
    """Position of a named object in the default map."""
    from navigate_server import grid_rasterizer
    path = os.path.join(os.environ.get('GEORG_MAP_DIR', '/root/georg_maps'),
                        os.environ.get('GEORG_DEFAULT_MAP', 'Nav_Test.yaml'))
    return grid_rasterizer.load_named_object_position(path, name)


def main():
    """Run the checks of one profile."""
    profile = sys.argv[1] if len(sys.argv) > 1 else 'mock'
    rclpy.init()
    node = Checker()
    ex = SingleThreadedExecutor()
    ex.add_node(node)
    threading.Thread(target=ex.spin, daemon=True).start()
    results = []

    def check(name, fn):
        t0 = time.time()
        try:
            detail = fn() or ''
            results.append(True)
            print(f'PASS  {name}  ({time.time() - t0:.1f} s) {detail}', flush=True)
        except Exception as exc:  # noqa: BLE001 - every failure is a failed check
            results.append(False)
            print(f'FAIL  {name}  ({time.time() - t0:.1f} s) {exc}', flush=True)

    def missions_listed():
        ids = node.call(node.list_cli, ListMissions.Request()).mission_ids
        if not ids:
            raise RuntimeError('no missions')
        return ', '.join(ids)

    def unknown_mission_rejected():
        resp = node.call(node.start_cli, StartMission.Request(mission_id='does_not_exist'))
        if resp.accepted:
            raise RuntimeError('unknown mission was accepted')
        return f'reason: {resp.reason}'

    check('missions are listed', missions_listed)
    check('unknown mission is rejected with a reason', unknown_mission_rejected)

    if profile == 'mock':
        def mock_mission():
            st = node.run_mission('mock_test', timeout=60)
            if st.state != MissionStatus.SUCCEEDED:
                raise RuntimeError(f'state {STATE[st.state]}: {st.message}')
            return st.message
        check('mock_test succeeds with the mock packages', mock_mission)

        def greeting():
            st = node.run_mission('greeting', timeout=60)
            if st.state != MissionStatus.SUCCEEDED:
                raise RuntimeError(f'state {STATE[st.state]}: {st.message}')
            return st.message
        check('greeting (speak via speech/say) succeeds with the mock packages', greeting)

    if profile == 'sim':
        def odom():
            if not wait_for(lambda: node.pose is not None, 15):
                raise RuntimeError('no /odom from the simulator')
            return f'pose {node.pose[0]:.2f}, {node.pose[1]:.2f}'

        def slam_map():
            if not wait_for(lambda: node.map is not None, 30):
                raise RuntimeError('no /map from slam_toolbox')
            info = node.map.info
            return f'{info.width}x{info.height} cells, {info.resolution} m'

        def seat():
            target = seat_position()
            start = node.pose   # run.sh restarts the simulator: start pose of the map
            st = node.run_mission('sim_seat', timeout=180)
            dist = math.dist(node.pose, target[:2])
            if st.state != MissionStatus.SUCCEEDED:
                raise RuntimeError(f'state {STATE[st.state]}: {st.message}')
            # the mission ends 'succeeded' even when a LOW task failed (Q21): check the pose
            if dist > 0.6:
                raise RuntimeError(f'mission succeeded but robot is {dist:.2f} m from the seat')
            return f'drove {math.dist(start, node.pose):.2f} m, ends {dist:.2f} m from the seat'

        def abort_stops():
            st = node.run_mission('sim_door', timeout=60, cancel_after=6.0)
            if st.state != MissionStatus.ABORTED:
                raise RuntimeError(f'state {STATE[st.state]} instead of ABORTED')
            time.sleep(1.5)
            stopped = node.pose
            time.sleep(1.5)
            moved = math.dist(node.pose, stopped)
            if moved > 0.02 or (node.speed or 0) > 0.01:
                raise RuntimeError(f'robot still moves after abort ({moved:.3f} m)')
            return f'moved {moved:.3f} m after stop'

        check('simulator publishes /odom', odom)
        check('SLAM builds a map in the simulator', slam_map)
        check('sim_seat: real navigation reaches the seat', seat)
        check('abort stops the drive', abort_stops)

        def reset():
            st = node.run_mission('sim_reset', timeout=30)
            if st.state != MissionStatus.SUCCEEDED:
                raise RuntimeError(f'state {STATE[st.state]}: {st.message}')
            time.sleep(1.0)
            dist = math.dist(node.pose, (1.0, 0.1))
            if dist > 0.05:
                raise RuntimeError(f'robot is {dist:.2f} m from the start after the reset')
            return f'back at the start ({dist:.3f} m)'
        check('sim_reset puts the robot back to the start', reset)

        def gestures():
            target = seat_position()
            st = node.run_mission('sim_gestures', timeout=240)
            if st.state != MissionStatus.SUCCEEDED:
                raise RuntimeError(f'state {STATE[st.state]}: {st.message}')
            dist = math.dist(node.pose, target[:2])
            if dist > 0.6:
                raise RuntimeError(f'mission succeeded but robot is {dist:.2f} m from the seat')
            return f'waved, drove, pointed; {dist:.2f} m from the seat'
        check('sim_gestures: poses and navigation', gestures)

    print(f'{sum(results)}/{len(results)} checks passed', flush=True)
    # exit right away: shutting rclpy down under the spinning thread aborts or prints errors
    os._exit(0 if all(results) else 1)


if __name__ == '__main__':
    main()
