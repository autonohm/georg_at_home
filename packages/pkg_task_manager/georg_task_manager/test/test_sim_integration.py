"""P3 simulation: simulator + SLAM + real navigation + task manager over real ROS.

Acceptance criteria from the plan: SLAM builds a map in the simulator, a mission with
the real navigation action runs through, abort stops the drive, the command gate
lets nothing through in profile sim.

Needs ROS, slam_toolbox and the built workspace; skipped otherwise.
Run with ``GEORG_ROS_TESTS=1`` (``pixi run test_sim`` on a Mac).
"""

import math
import os
import sys
import threading
import time

import pytest

sys.path.insert(0, os.path.dirname(__file__))
import conftest  # noqa: E402, I100

if os.environ.get('GEORG_ROS_TESTS') != '1' or 'rclpy' in conftest.STUBBED:
    pytest.skip('ROS integration tests: set GEORG_ROS_TESTS=1 in a ROS environment',
                allow_module_level=True)

from geometry_msgs.msg import Twist  # noqa: E402
from georg_task_manager_msgs.msg import MissionStatus  # noqa: E402
from nav_msgs.msg import OccupancyGrid, Odometry  # noqa: E402
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy  # noqa: E402
from ros_helpers import _spawn, _stop, NS, REPO  # noqa: E402

# sim2d (stage 1) or simmj (MuJoCo, stage 2)
SIMULATOR = os.environ.get('GEORG_SIMULATOR', 'sim2d')
SEAT = (6.134, 0.093)
DOOR = (0.264, 0.105)


@pytest.fixture(scope='module')
def ros_profile():
    return 'sim'


@pytest.fixture(scope='module')
def sim_stack(env, bridge):
    """Start simulator, SLAM and the real navigation servers once for the module."""
    maps = env['GEORG_MAP_DIR']
    procs = [
        _spawn(['ros2', 'run', 'georg_sim', SIMULATOR, '--ros-args', '-r', f'__ns:={NS}',
                '-p', f'map_file:={os.path.join(maps, "Nav_Test.yaml")}'],
               os.path.join(env['TMP'], 'sim.log'), env),
        _spawn(['ros2', 'launch', 'slam_sim.launch.py'], os.path.join(env['TMP'], 'slam.log'),
               env, cwd=os.path.join(REPO, 'pkg_slam', 'config')),
        _spawn(['ros2', 'launch', os.path.join(REPO, 'pkg_navigation', 'config',
                                               'navigation.launch.py')],
               os.path.join(env['TMP'], 'nav.log'), env),
    ]
    time.sleep(5.0)
    yield procs
    for p in procs:
        _stop(p)


class Robot:
    """Latest odometry and map of the simulated robot, plus cmd_vel."""

    def __init__(self, node):
        self.pose = None
        self.map = None
        self._lock = threading.Lock()
        node.create_subscription(Odometry, f'{NS}/odom', self._on_odom, 10)
        map_qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                             reliability=ReliabilityPolicy.RELIABLE)
        # slam_toolbox publishes the map absolute (/map), not in the robot namespace
        node.create_subscription(OccupancyGrid, '/map', self._on_map, map_qos)
        self.cmd = node.create_publisher(Twist, f'{NS}/cmd_vel', 10)

    def _on_odom(self, msg):
        with self._lock:
            self.pose = (msg.pose.pose.position.x, msg.pose.pose.position.y)

    def _on_map(self, msg):
        with self._lock:
            self.map = msg

    def drive(self, vx=0.0, wz=0.0, seconds=1.0):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            msg = Twist()
            msg.linear.x, msg.angular.z = vx, wz
            self.cmd.publish(msg)
            time.sleep(0.05)

    def wait_pose(self, timeout=10.0):
        end = time.monotonic() + timeout
        while self.pose is None:
            assert time.monotonic() < end, 'no odom from the simulator'
            time.sleep(0.05)
        return self.pose


@pytest.fixture(scope='module')
def robot(client, sim_stack):
    return Robot(client.node)


def _dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def test_simulator_follows_cmd_vel_and_stops_without_commands(robot):
    start = robot.wait_pose()
    robot.drive(vx=0.3, seconds=1.0)
    time.sleep(0.8)                      # cmd timeout 0.5 s
    moved = robot.pose
    assert 0.15 < moved[0] - start[0] < 0.5
    time.sleep(1.0)
    assert _dist(robot.pose, moved) < 0.01


def test_slam_builds_a_map(robot):
    robot.drive(wz=0.8, seconds=4.0)     # look around
    end = time.monotonic() + 40
    while True:
        grid = robot.map
        occupied = sum(1 for v in grid.data if v > 50) if grid is not None else 0
        if occupied > 100:
            break
        assert time.monotonic() < end, f'map has only {occupied} occupied cells'
        time.sleep(1.0)
    assert grid.info.resolution == pytest.approx(0.05)


def test_mission_with_real_navigation_reaches_the_seat(client, mocks, robot):
    mocks.run('sim_mocks')               # navigation is real, the rest mocked
    response = client.start('sim_seat')
    assert response.accepted, response.reason
    final = client.wait_final(response.burr_app_id, timeout=150)
    assert final.state == MissionStatus.SUCCEEDED, final.message
    assert _dist(robot.pose, SEAT) < 0.8, robot.pose


def test_abort_stops_the_drive(client, mocks, robot):
    mocks.run('sim_mocks')
    start = robot.wait_pose()
    response = client.start('sim_door')
    assert response.accepted, response.reason
    end = time.monotonic() + 40
    while _dist(robot.pose, start) < 0.5:        # wait until it really drives
        assert time.monotonic() < end, 'robot does not drive'
        time.sleep(0.1)
    assert client.cancel().accepted
    final = client.wait_final(response.burr_app_id, timeout=10)
    assert final.state == MissionStatus.ABORTED
    time.sleep(1.0)                              # cmd timeout of the simulator
    stopped = robot.pose
    time.sleep(1.5)
    assert _dist(robot.pose, stopped) < 0.02, 'robot still moves after abort'
    assert _dist(robot.pose, DOOR) > 1.0         # it really stopped on the way


def test_command_gate_lets_nothing_through_in_sim(env, client, robot):
    gate = _spawn(['ros2', 'run', 'command_gate', 'command_gate', '--ros-args',
                   '-r', f'__ns:={NS}'], os.path.join(env['TMP'], 'gate.log'), env)
    try:
        received = []
        client.node.create_subscription(Twist, f'{NS}/cmd_vel/gated', received.append, 10)
        time.sleep(3.0)
        robot.drive(vx=0.05, seconds=1.5)
        time.sleep(0.5)
        assert received == []
        assert 'CLOSED' in open(os.path.join(env['TMP'], 'gate.log')).read()
    finally:
        _stop(gate)
