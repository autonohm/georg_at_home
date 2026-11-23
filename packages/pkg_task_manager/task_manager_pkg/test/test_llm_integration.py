"""P6 over real ROS: operating modes, LLM planner, guard rails, approval (profile mock).

The LLM is a scripted OpenAI-compatible HTTP server (ros_helpers.FakeLLMServer), so every
acceptance criterion can be checked deterministically. The same tests run against a real
local LLM in test_llm_real.py.

Needs ROS and the built workspace (GEORG_ROS_TESTS=1).
"""

import json
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

from georg_task_manager_msgs.msg import MissionStatus  # noqa: E402, I100
from georg_task_manager_msgs.srv import ApprovePlan, Instruct, SetMode  # noqa: E402
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy  # noqa: E402
import ros_helpers  # noqa: E402
from std_msgs.msg import String  # noqa: E402

NS = ros_helpers.NS
GESTURE = {'task': 'gesture', 'args': {'mode': 'look_at', 'vx': -1000.0, 'vy': 0.0, 'vz': 100.0}}


def plan(*steps, reason='ok'):
    return {'decision': 'plan', 'steps': list(steps), 'reason': reason}


def say(decision, reason='ok'):
    return {'decision': decision, 'steps': [], 'reason': reason}


@pytest.fixture(scope='module')
def fake_llm():
    server = ros_helpers.FakeLLMServer()
    yield server
    server.close()


@pytest.fixture(scope='module')
def env(ros_profile, fake_llm):
    e = ros_helpers.make_env(ros_profile)
    e['GEORG_LLM_URL'] = fake_llm.url
    e['GEORG_DECISION_LOG_DIR'] = os.path.join(e['TMP'], 'decisions')
    return e


class Operator:
    """Lichtblick-like operator: mode, instructions, approvals, plan topic."""

    def __init__(self, client):
        node = client.node
        self.client = client
        self.mode_cli = node.create_client(SetMode, f'{NS}/task_manager/set_mode')
        self.instruct_cli = node.create_client(Instruct, f'{NS}/task_manager/instruct')
        self.approve_cli = node.create_client(ApprovePlan, f'{NS}/task_manager/approve_plan')
        self.plans = []
        self._lock = threading.Lock()
        qos = QoSProfile(depth=10, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                         reliability=ReliabilityPolicy.RELIABLE)
        node.create_subscription(String, f'{NS}/task_manager/plan', self._on_plan, qos)

    def _on_plan(self, msg):
        with self._lock:
            self.plans.append(json.loads(msg.data))

    def mode(self, mode):
        return self.client.call(self.mode_cli, SetMode.Request(mode=mode))

    def instruct(self, text):
        return self.client.call(self.instruct_cli, Instruct.Request(text=text))

    def approve(self, ok=True):
        return self.client.call(self.approve_cli, ApprovePlan.Request(approve=ok))

    def wait_plan(self, predicate, timeout=20.0):
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            with self._lock:
                if any(predicate(p) for p in self.plans):
                    return
            time.sleep(0.05)
        raise AssertionError(f'no such plan message: {self.plans[-3:]}')


@pytest.fixture(scope='module')
def operator(client):
    return Operator(client)


def test_after_start_mission_mode_and_llm_does_nothing(client, operator, fake_llm):
    operator.wait_plan(lambda p: p.get('mode') == 'mission')
    response = operator.instruct('greet the guest')
    assert not response.accepted and 'switch to an LLM mode' in response.reason
    assert fake_llm.requests == []
    assert not operator.mode('party').accepted


def test_llm_plans_and_burr_executes_without_intervention(client, operator, fake_llm, mocks):
    mocks.run('all_ok')
    assert operator.mode('llm').accepted
    fake_llm.answers = [plan({'block': 'wait_for_guest'},
                             {'task': 'navigate_object', 'args': {'object_name': 'Seat'}}),
                        say('continue'), say('done', 'guest greeted')]
    response = operator.instruct('a guest arrives, bring them to the seat')
    assert response.accepted, response.reason
    final = client.wait_final(response.burr_app_id, timeout=40)
    assert final.state == MissionStatus.SUCCEEDED, final.message
    assert 'goal reached' in final.message
    log = mocks.text()
    assert 'audio/listen: goal received' in log
    assert 'pib_gestures_interface: goal received' in log
    assert 'navigate_to_pose: goal received' in log
    # after every task the result went back to the LLM: 3 decisions
    assert len(fake_llm.requests) == 3
    third = json.loads(fake_llm.requests[2]['messages'][1]['content'])
    assert [h['result'] for h in third['history']] == ['ok', 'ok']
    assert 'Seat' in third['places']
    assert fake_llm.requests[0]['temperature'] == 0.0
    operator.wait_plan(lambda p: p.get('current') == 'block wait_for_guest')


def test_invalid_plans_end_in_idle(client, operator, fake_llm, mocks):
    fake_llm.requests.clear()
    fake_llm.answers = ['nonsense', plan({'task': 'teleport'}), {'decision': 'maybe'}]
    response = operator.instruct('do something')
    final = client.wait_final(response.burr_app_id, timeout=30)
    assert final.state == MissionStatus.FAILED
    assert 'no valid plan after 3 attempts' in final.message
    assert len(fake_llm.requests) == 3
    assert 'rejected' in fake_llm.requests[1]['messages'][-1]['content']


def test_failed_task_leads_to_clean_abort(client, operator, fake_llm, mocks):
    mocks.run('one_fails')                       # gestures fail
    fake_llm.answers = [plan(GESTURE), say('abort', 'gesture package broken')]
    response = operator.instruct('look at the door')
    final = client.wait_final(response.burr_app_id, timeout=30)
    assert final.state == MissionStatus.ABORTED
    assert 'gesture package broken' in final.message


def test_failed_task_leads_to_replan(client, operator, fake_llm, mocks):
    mocks.run('retry_then_ok')                   # first gesture fails, then gestures work
    fake_llm.answers = [plan(GESTURE), plan({'block': 'greet_guest'}, reason='try the block'),
                        say('done')]
    response = operator.instruct('greet')
    final = client.wait_final(response.burr_app_id, timeout=30)
    assert final.state == MissionStatus.SUCCEEDED, final.message


def test_operator_feedback_reaches_the_next_decision(client, operator, fake_llm, mocks):
    mocks.run('slow_drive')                      # driving takes 3 s
    fake_llm.requests.clear()
    fake_llm.answers = [plan({'task': 'navigate_object', 'args': {'object_name': 'Seat'}}),
                        say('done')]
    response = operator.instruct('go to the seat')
    client.wait_for(lambda m: m.burr_app_id == response.burr_app_id
                    and m.current_task == 'navigate_object', timeout=20)
    assert operator.instruct('the guest left').accepted        # feedback while running
    final = client.wait_final(response.burr_app_id, timeout=30)
    assert final.state == MissionStatus.SUCCEEDED
    second = json.loads(fake_llm.requests[1]['messages'][1]['content'])
    assert second['operator_feedback'] == 'the guest left'
    first = json.loads(fake_llm.requests[0]['messages'][1]['content'])
    assert first['operator_feedback'] == ''


def test_approval_mode(client, operator, fake_llm, mocks):
    mocks.run('all_ok')
    assert operator.mode('llm_approval').accepted
    fake_llm.answers = [plan(GESTURE), say('done')]
    response = operator.instruct('look at the door')
    operator.wait_plan(lambda p: p.get('waiting_for_approval'))
    time.sleep(0.5)
    assert 'pib_gestures_interface: goal received' not in mocks.text()   # nothing yet
    assert operator.approve(True).accepted
    final = client.wait_final(response.burr_app_id, timeout=30)
    assert final.state == MissionStatus.SUCCEEDED

    fake_llm.answers = [plan(GESTURE)]
    response = operator.instruct('look at the door again')
    operator.wait_plan(lambda p: p.get('waiting_for_approval')
                       and p.get('reason') == 'ok' and response.burr_app_id)
    time.sleep(0.5)
    assert operator.approve(False).accepted
    final = client.wait_final(response.burr_app_id, timeout=30)
    assert final.state == MissionStatus.ABORTED and 'rejected' in final.message
    assert not operator.approve(True).accepted                # nothing waiting anymore


def test_llm_unreachable_is_rejected(client, operator, fake_llm):
    fake_llm.offline = True
    try:
        response = operator.instruct('anything')
        assert not response.accepted and 'not reachable' in response.reason
    finally:
        fake_llm.offline = False
    assert operator.mode('mission').accepted


def test_every_decision_is_logged(env):
    logs = os.listdir(env['GEORG_DECISION_LOG_DIR'])
    records = [json.loads(line) for name in logs
               for line in open(os.path.join(env['GEORG_DECISION_LOG_DIR'], name))]
    assert records and all({'prompt_version', 'model', 'input', 'attempts', 'decision'}
                           <= set(r) for r in records)
