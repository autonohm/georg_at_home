"""P5: record -> raw sensors only -> replay with live SLAM and Burr, twice the same.

1. record a drive in the simulator while SLAM runs (like on the robot: /tf has map -> odom)
2. strip the recording to raw sensors (pkg_slam/tools/mcap_raw_only.py)
3. replay it twice (ros2 bag play --clock, SLAM with use_sim_time, task manager + mocks)
   and run the same mission each time
4. both Burr runs must be identical (decision replay comparison), SLAM builds a map

Needs ROS, slam_toolbox, rosbag2 with MCAP and the built workspace (GEORG_ROS_TESTS=1).
"""

import os
import subprocess
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(__file__))
import conftest  # noqa: E402, I100

if os.environ.get('GEORG_ROS_TESTS') != '1' or 'rclpy' in conftest.STUBBED:
    pytest.skip('ROS integration tests: set GEORG_ROS_TESTS=1 in a ROS environment',
                allow_module_level=True)

from geometry_msgs.msg import Twist  # noqa: E402
from georg_task_manager_msgs.msg import MissionStatus  # noqa: E402
from nav_msgs.msg import OccupancyGrid  # noqa: E402
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy  # noqa: E402
from rclpy.serialization import deserialize_message  # noqa: E402
import rosbag2_py  # noqa: E402
from ros_helpers import _spawn, _stop, NS, REPO  # noqa: E402, I100
from tf2_msgs.msg import TFMessage  # noqa: E402

SLAM_CONFIG = os.path.join(REPO, 'pkg_slam', 'config')
sys.path.insert(0, os.path.join(REPO, 'pkg_slam', 'tools'))
sys.path.insert(0, os.path.join(REPO, '..', 'tests', 'decision_replay'))
import mcap_raw_only  # noqa: E402, I100
import replay as decision_replay  # noqa: E402


@pytest.fixture(scope='module')
def ros_profile():
    return 'mcap'


def _topics(bag):
    reader = rosbag2_py.SequentialReader()
    reader.open(rosbag2_py.StorageOptions(uri=bag, storage_id='mcap'),
                rosbag2_py.ConverterOptions('cdr', 'cdr'))
    names, map_tf = set(), 0
    while reader.has_next():
        name, data, _ = reader.read_next()
        names.add(name)
        if name == '/tf':
            map_tf += sum(1 for t in deserialize_message(data, TFMessage).transforms
                          if t.header.frame_id == 'map')
    return names, map_tf


@pytest.fixture(scope='module')
def recording(env, client):
    """Drive in the simulator for ~15 s with SLAM running and record everything."""
    tmp = env['TMP']
    maps = env['GEORG_MAP_DIR']
    sim = _spawn(['ros2', 'run', 'georg_sim', 'sim2d', '--ros-args', '-r', f'__ns:={NS}',
                  '-p', f'map_file:={os.path.join(maps, "Nav_Test.yaml")}'],
                 os.path.join(tmp, 'rec_sim.log'), env)
    slam = _spawn(['ros2', 'launch', 'slam_sim.launch.py'], os.path.join(tmp, 'rec_slam.log'),
                  env, cwd=SLAM_CONFIG)
    time.sleep(4)
    bag = os.path.join(tmp, 'drive')
    rec = _spawn(['ros2', 'bag', 'record', '-s', 'mcap', '-o', bag, '/tf', '/tf_static',
                  f'{NS}/merged_scan', f'{NS}/scan', f'{NS}/odom', '/map'],
                 os.path.join(tmp, 'rec_bag.log'), env)
    time.sleep(3)
    cmd = client.node.create_publisher(Twist, f'{NS}/cmd_vel', 10)
    for vx, wz, seconds in ((0.0, 0.8, 4.0), (0.3, 0.0, 3.0), (0.0, -0.8, 4.0)):
        end = time.monotonic() + seconds
        while time.monotonic() < end:
            msg = Twist()
            msg.linear.x, msg.angular.z = vx, wz
            cmd.publish(msg)
            time.sleep(0.05)
    time.sleep(2)
    for p in (rec, slam, sim):
        _stop(p)
    return bag


def test_recording_has_slam_output_and_raw_copy_has_not(recording, env):
    names, map_tf = _topics(recording)
    assert {f'{NS}/merged_scan', f'{NS}/odom', '/tf'} <= names
    assert map_tf > 0                                   # SLAM's map -> odom was recorded
    raw = os.path.join(env['TMP'], 'drive_raw')
    counts = mcap_raw_only.filter_bag(recording, raw)
    assert counts[f'{NS}/merged_scan'] > 50
    names, map_tf = _topics(raw)
    assert '/map' not in names
    assert map_tf == 0                                  # map -> odom removed


def _play_once(env, client, mocks, label):
    """Replay the raw recording with live SLAM, run mock_test; return its Burr app dir."""
    raw = os.path.join(env['TMP'], 'drive_raw')
    grids = []
    qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                     reliability=ReliabilityPolicy.RELIABLE)
    sub = client.node.create_subscription(OccupancyGrid, '/map', grids.append, qos)
    slam = _spawn(['ros2', 'launch', 'slam_mcap.launch.py'],
                  os.path.join(env['TMP'], f'{label}_slam.log'), env, cwd=SLAM_CONFIG)
    mocks.run('mcap')
    time.sleep(3)
    player = _spawn(['ros2', 'bag', 'play', raw, '--clock', '100'],
                    os.path.join(env['TMP'], f'{label}_play.log'), env)
    try:
        time.sleep(3)
        response = client.start('mock_test')
        assert response.accepted, response.reason
        final = client.wait_final(response.burr_app_id, timeout=60)
        assert final.state == MissionStatus.SUCCEEDED, final.message
        player.wait(timeout=60)                          # replay to the end
        end = time.monotonic() + 20
        while not grids:
            assert time.monotonic() < end, 'SLAM built no map from the replay'
            time.sleep(0.5)
        assert sum(1 for v in grids[-1].data if v > 50) > 50
        return os.path.join(env['GEORG_BURR_STORAGE_DIR'], 'georg_task_manager',
                            response.burr_app_id)
    finally:
        client.node.destroy_subscription(sub)
        _stop(player)
        _stop(slam)


def test_same_recording_gives_the_same_task_sequence_twice(
        recording, env, client, mocks, bridge):
    if not os.path.exists(os.path.join(env['TMP'], 'drive_raw')):
        mcap_raw_only.filter_bag(recording, os.path.join(env['TMP'], 'drive_raw'))
    first = decision_replay.load_recording(_play_once(env, client, mocks, 'play1'))
    second = decision_replay.load_recording(_play_once(env, client, mocks, 'play2'))
    assert first.steps and first.steps == second.steps
    assert decision_replay.compare(first, second) == []
    # and the recorded run can be replayed decision by decision
    assert decision_replay.replay(os.path.join(env['GEORG_BURR_STORAGE_DIR'],
                                               'georg_task_manager', first.app_id), runs=2) == []


def test_player_is_the_only_source_of_sensor_topics(recording, env, client, mocks):
    """One source per topic: in mcap the mocks publish no odom (scenario mcap)."""
    mocks.run('mcap')
    time.sleep(1)
    out = subprocess.run(['ros2', 'topic', 'info', f'{NS}/odom'], env=env, capture_output=True,
                         text=True, timeout=30).stdout
    assert 'Publisher count: 0' in out


def test_continuous_recording_contains_status_with_burr_id(env, client, mocks, bridge):
    """The recorder of compose (same arguments) captures /task_manager/* with burr_app_id."""
    mocks.run('mcap')
    bag = os.path.join(env['TMP'], 'task_manager_rec')
    rec = _spawn(['ros2', 'bag', 'record', '-s', 'mcap', '--max-bag-duration', '3600', '-o', bag,
                  '--regex', f'{NS}/task_manager/.*|{NS}/task/current_task'],
                 os.path.join(env['TMP'], 'recorder.log'), env)
    try:
        time.sleep(3)
        response = client.start('mock_test')
        assert response.accepted, response.reason
        client.wait_final(response.burr_app_id, timeout=30)
        time.sleep(1)
    finally:
        _stop(rec)
    reader = rosbag2_py.SequentialReader()
    reader.open(rosbag2_py.StorageOptions(uri=bag, storage_id='mcap'),
                rosbag2_py.ConverterOptions('cdr', 'cdr'))
    ids, topics = set(), set()
    while reader.has_next():
        name, data, _ = reader.read_next()
        topics.add(name)
        if name == f'{NS}/task_manager/status':
            ids.add(deserialize_message(data, MissionStatus).burr_app_id)
    assert {f'{NS}/task_manager/status', f'{NS}/task/current_task'} <= topics
    assert response.burr_app_id in ids
