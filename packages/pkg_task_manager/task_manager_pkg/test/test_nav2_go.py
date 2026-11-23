"""Nav2 adapter (tasks/nav2_go.py) with a fake action client (no ROS graph needed)."""

import asyncio
import math
from types import SimpleNamespace

from action_msgs.msg import GoalStatus
import pytest
from task_manager.tasks import nav2_go


class FakeFuture:
    def __init__(self, value=None, done=True):
        self._value, self._done, self._callbacks = value, done, []

    def add_done_callback(self, cb):
        if self._done:
            cb(self)
        else:
            self._callbacks.append(cb)

    def result(self):
        return self._value


class FakeClient:
    """Loses the first ``lost`` goal responses, then accepts and finishes with ``status``."""

    def __init__(self, status=GoalStatus.STATUS_SUCCEEDED, lost=0, server=True):
        self.status, self.lost, self.server, self.sent = status, lost, server, 0

    def wait_for_server(self, timeout_sec):
        return self.server

    def send_goal_async(self, goal):
        self.sent += 1
        if self.sent <= self.lost:
            return FakeFuture(done=False)
        result = SimpleNamespace(status=self.status,
                                 result=SimpleNamespace(error_code=0, error_msg=''))
        handle = SimpleNamespace(accepted=True,
                                 get_result_async=lambda: FakeFuture(result),
                                 cancel_goal_async=lambda: FakeFuture(None))
        return FakeFuture(handle)


def run(client, **kw):
    goal = nav2_go.make_goal(1.0, 2.0, 0.5)
    return asyncio.run(nav2_go.nav2_go(client, goal, timeout=5.0, log=lambda _: None, **kw))


def test_goal_pose_and_facing_yaw():
    goal = nav2_go.make_goal(1.0, 2.0, math.pi / 2)
    assert goal.pose.header.frame_id == 'map'
    assert (goal.pose.pose.position.x, goal.pose.pose.position.y) == (1.0, 2.0)
    assert goal.pose.pose.orientation.z == pytest.approx(math.sin(math.pi / 4))
    # driving along +x: pib (front offset pi/2) faces +x
    assert nav2_go.facing_yaw((0, 0), (1, 0)) == pytest.approx(math.pi / 2)


def test_succeeded_and_failed():
    assert run(FakeClient()) is True
    assert run(FakeClient(status=GoalStatus.STATUS_ABORTED)) is False
    assert run(FakeClient(server=False)) is False


def test_lost_goal_response_is_sent_again(monkeypatch):
    monkeypatch.setattr(nav2_go, 'GOAL_RESPONSE_TIMEOUT_S', 0.05)
    client = FakeClient(lost=2)
    assert run(client) is True
    assert client.sent == 3
    assert run(FakeClient(lost=3)) is False
