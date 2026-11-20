"""P2 mock integration: task manager node + mock packages over real ROS.

Mandatory scenarios from the plan: everything succeeds, one task fails, timeout,
abort during a task, package unreachable at start, ten missions in a row.

Needs ROS and the built workspace; skipped otherwise. Run with
``GEORG_ROS_TESTS=1`` (``pixi run test_ros`` on a Mac, or inside the container).
"""

import os
import sys
import time

import pytest

sys.path.insert(0, os.path.dirname(__file__))
import conftest  # noqa: E402, I100

if os.environ.get('GEORG_ROS_TESTS') != '1' or 'rclpy' in conftest.STUBBED:
    pytest.skip('ROS integration tests: set GEORG_ROS_TESTS=1 in a ROS environment',
                allow_module_level=True)

from georg_task_manager_msgs.msg import MissionStatus  # noqa: E402, I100
from georg_task_manager_msgs.srv import ListMissions  # noqa: E402


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
