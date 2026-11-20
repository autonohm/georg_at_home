"""P2 mock integration: task manager node + mock packages over real ROS.

Mandatory scenarios from the plan: everything succeeds, one task fails, timeout,
abort during a task, package unreachable at start, ten missions in a row.

Needs ROS and the built workspace; skipped otherwise. Run with
``GEORG_ROS_TESTS=1`` (``pixi run test_ros`` on a Mac, or inside the container).
"""

import os
import random
import signal
import subprocess
import sys
import tempfile
import threading
import time

import pytest

sys.path.insert(0, os.path.dirname(__file__))
import conftest  # noqa: E402, I100

if os.environ.get('GEORG_ROS_TESTS') != '1' or 'rclpy' in conftest.STUBBED:
    pytest.skip('ROS integration tests: set GEORG_ROS_TESTS=1 in a ROS environment',
                allow_module_level=True)

import rclpy  # noqa: E402
from rclpy.executors import SingleThreadedExecutor  # noqa: E402
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy  # noqa: E402

from georg_task_manager_msgs.msg import MissionStatus  # noqa: E402, I100
from georg_task_manager_msgs.srv import (  # noqa: E402
    CancelMission, ListMissions, StartMission)

NS = '/georg'
FINAL = {MissionStatus.SUCCEEDED, MissionStatus.FAILED, MissionStatus.ABORTED}
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))


def _spawn(args, log_path, env):
    log = open(log_path, 'w')
    return subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT, env=env,
                            start_new_session=True)


def _stop(proc):
    if proc.poll() is None:
        os.killpg(proc.pid, signal.SIGINT)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL)
            proc.wait()


class Client:
    """Test-side ROS node: service clients and the latest status."""

    def __init__(self):
        self.node = rclpy.create_node('task_manager_test')
        qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                         reliability=ReliabilityPolicy.RELIABLE)
        self.statuses = []
        self._lock = threading.Lock()
        self.node.create_subscription(MissionStatus, f'{NS}/task_manager/status',
                                      self._on_status, qos)
        self.start_cli = self.node.create_client(StartMission, f'{NS}/task_manager/start')
        self.cancel_cli = self.node.create_client(CancelMission, f'{NS}/task_manager/cancel')
        self.list_cli = self.node.create_client(ListMissions, f'{NS}/task_manager/list_missions')
        self.executor = SingleThreadedExecutor()
        self.executor.add_node(self.node)
        self._thread = threading.Thread(target=self.executor.spin, daemon=True)
        self._thread.start()

    def _on_status(self, msg):
        with self._lock:
            self.statuses.append(msg)

    def last(self):
        with self._lock:
            return self.statuses[-1] if self.statuses else None

    def call(self, client, request, timeout=15.0):
        assert client.wait_for_service(timeout_sec=timeout), 'service not available'
        future = client.call_async(request)
        end = time.monotonic() + timeout
        while not future.done():
            assert time.monotonic() < end, 'service call timed out'
            time.sleep(0.02)
        return future.result()

    def start(self, mission_id='mock_test'):
        return self.call(self.start_cli, StartMission.Request(mission_id=mission_id))

    def cancel(self):
        return self.call(self.cancel_cli, CancelMission.Request())

    def wait_for(self, predicate, timeout=30.0):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            msg = self.last()
            if msg is not None and predicate(msg):
                return msg
            time.sleep(0.05)
        raise AssertionError(f'timeout, last status: {self.last()}')

    def wait_final(self, app_id, timeout=30.0):
        return self.wait_for(lambda m: m.burr_app_id == app_id and m.state in FINAL, timeout)

    def close(self):
        self.executor.shutdown()
        self.node.destroy_node()


@pytest.fixture(scope='module')
def env():
    tmp = tempfile.mkdtemp(prefix='georg_ros_test_')
    e = dict(os.environ,
             ROS_DOMAIN_ID=str(random.randint(60, 100)),
             GEORG_MAP_DIR=os.path.join(REPO, 'pkg_slam', 'maps'),
             GEORG_BURR_STORAGE_DIR=os.path.join(tmp, 'burr'),
             GEORG_PROFILE='mock',
             PYTHONUNBUFFERED='1',
             RCUTILS_LOGGING_BUFFERED_STREAM='0')
    os.environ['ROS_DOMAIN_ID'] = e['ROS_DOMAIN_ID']
    e['TMP'] = tmp
    return e


@pytest.fixture(scope='module')
def bridge(env):
    proc = _spawn(['ros2', 'run', 'georg_task_manager', 'task_manager',
                   '--ros-args', '-r', f'__ns:={NS}'], os.path.join(env['TMP'], 'bridge.log'), env)
    yield proc
    _stop(proc)


@pytest.fixture(scope='module')
def client(bridge):
    rclpy.init()
    c = Client()
    c.wait_for(lambda m: True, timeout=20)   # first status from the node
    yield c
    c.close()
    rclpy.shutdown()


class Mocks:
    def __init__(self, env):
        self.env = env
        self.proc = None
        self.log = ''

    def run(self, scenario):
        self.stop()
        self.log = os.path.join(self.env['TMP'], f'mock_{scenario}.log')
        self.proc = _spawn(['ros2', 'run', 'georg_task_manager', 'mock_packages',
                            '--scenario', scenario, '--ros-args', '-r', f'__ns:={NS}'],
                           self.log, self.env)
        end = time.monotonic() + 20
        while 'mock packages ready' not in open(self.log).read():
            assert time.monotonic() < end, open(self.log).read()
            time.sleep(0.1)
        time.sleep(1.0)   # let discovery settle

    def text(self):
        return open(self.log).read()

    def wait_text(self, needle, count=1, timeout=5.0):
        """Wait until ``needle`` appears ``count`` times in the mock log (logs are async)."""
        end = time.monotonic() + timeout
        while self.text().count(needle) < count:
            assert time.monotonic() < end, f'{needle!r} x{count} not in mock log:\n{self.text()}'
            time.sleep(0.05)
        return self.text().count(needle)

    def stop(self):
        if self.proc is not None:
            _stop(self.proc)
            self.proc = None
            time.sleep(0.5)


@pytest.fixture(scope='module')
def mocks(env):
    m = Mocks(env)
    yield m
    m.stop()


# --- tests (in this order) --------------------------------------------------

def test_starts_in_idle_and_lists_missions(client):
    assert client.statuses[0].state == MissionStatus.IDLE
    response = client.call(client.list_cli, ListMissions.Request())
    assert 'digital_festival' in response.mission_ids
    assert 'mock_test' in response.mission_ids


def test_unknown_mission_is_rejected(client, mocks):
    mocks.run('all_ok')
    response = client.start('no_such_mission')
    assert not response.accepted and 'unknown mission' in response.reason


def test_cancel_without_mission_is_rejected(client):
    response = client.cancel()
    assert not response.accepted and 'no mission running' in response.reason


def test_everything_succeeds(client, mocks):
    mocks.run('all_ok')
    response = client.start()
    assert response.accepted, response.reason
    final = client.wait_final(response.burr_app_id)
    assert final.state == MissionStatus.SUCCEEDED
    assert final.mission_id == 'mock_test'


def test_one_task_fails(client, mocks):
    mocks.run('one_fails')          # gesture is CRITICAL in mock_test
    response = client.start()
    final = client.wait_final(response.burr_app_id)
    assert final.state == MissionStatus.FAILED
    assert 'critical' in final.message
    assert mocks.wait_text('pib_gestures_interface: goal received', 4) == 4  # 1 + 3 retries


def test_retry_then_success(client, mocks):
    mocks.run('retry_then_ok')
    response = client.start()
    final = client.wait_final(response.burr_app_id)
    assert final.state == MissionStatus.SUCCEEDED
    assert mocks.wait_text('pib_gestures_interface: goal received', 2) == 2


def test_timeout_cancels_goal_and_mission_goes_on(client, mocks):
    mocks.run('timeout')            # listen never answers; LOW -> discarded
    started = time.monotonic()
    response = client.start()
    final = client.wait_final(response.burr_app_id, timeout=40)
    assert final.state == MissionStatus.SUCCEEDED
    assert time.monotonic() - started >= 4.5          # timeout_sec 3 + 2
    mocks.wait_text('audio/listen: canceled')   # the goal was cancelled, not abandoned


def test_abort_during_task(client, mocks):
    mocks.run('abort')              # drive takes 30 s
    response = client.start()
    client.wait_for(lambda m: m.burr_app_id == response.burr_app_id
                    and 'NavigateObject' in m.current_task, timeout=20)
    time.sleep(1.0)                 # drive is running now
    second = client.start()
    assert not second.accepted and 'still running' in second.reason
    asked = time.monotonic()
    assert client.cancel().accepted
    final = client.wait_final(response.burr_app_id, timeout=10)
    assert final.state == MissionStatus.ABORTED
    assert time.monotonic() - asked < 3.0             # plan: abort within 2 s (+ margin)
    mocks.wait_text('nav/drive_route: canceled')


def test_package_unreachable_at_start(client, mocks):
    mocks.run('unreachable')        # no drive server
    response = client.start()
    assert not response.accepted
    assert 'nav/drive_route' in response.reason


def test_ten_missions_in_a_row_without_restart(client, mocks, bridge):
    mocks.run('all_ok')
    ids = set()
    for _ in range(10):
        response = client.start()
        assert response.accepted, response.reason
        assert client.wait_final(response.burr_app_id).state == MissionStatus.SUCCEEDED
        ids.add(response.burr_app_id)
    assert len(ids) == 10
    assert bridge.poll() is None    # same process all along
