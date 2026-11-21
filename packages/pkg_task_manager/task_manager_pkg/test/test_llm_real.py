"""P6 with a real local LLM (llama.cpp, OpenAI-compatible endpoint at GEORG_LLM_URL).

- In profile mock the LLM plans a mission and Burr executes it without intervention.
- Every decision of that run is valid (guard rails) and logged.
- Decision replay with the fixed prompt is stable: same input -> same structured decision.

Needs ROS, the built workspace and a running LLM endpoint:
GEORG_ROS_TESTS=1 GEORG_LLM_REAL=1
(on a Mac: pixi run -e llm llm_server, then pixi run test_llm_real).
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(__file__))
import conftest  # noqa: E402, I100

if os.environ.get('GEORG_ROS_TESTS') != '1' or os.environ.get('GEORG_LLM_REAL') != '1' \
        or 'rclpy' in conftest.STUBBED:
    pytest.skip('real LLM tests: set GEORG_ROS_TESTS=1 and GEORG_LLM_REAL=1',
                allow_module_level=True)

from georg_task_manager_msgs.msg import MissionStatus  # noqa: E402, I100
from task_manager.planner.llm_client import LLMClient  # noqa: E402, I100
import ros_helpers  # noqa: E402, I100
from test_llm_integration import Operator  # noqa: E402

REPO = ros_helpers.REPO
sys.path.insert(0, os.path.join(REPO, '..', 'tests', 'decision_replay'))
import replay as decision_replay  # noqa: E402, I100

GOAL = 'A guest rings the doorbell. Greet the guest and bring them to the seat.'


@pytest.fixture(scope='module')
def env(ros_profile):
    if not LLMClient().available():
        pytest.skip(f'no LLM endpoint at {LLMClient().config.url}')
    e = ros_helpers.make_env(ros_profile)
    e['GEORG_DECISION_LOG_DIR'] = os.path.join(e['TMP'], 'decisions')
    return e


@pytest.fixture(scope='module')
def operator(client):
    return Operator(client)


def _decisions(env):
    folder = env['GEORG_DECISION_LOG_DIR']
    files = [os.path.join(folder, f) for f in sorted(os.listdir(folder))]
    return files, [json.loads(line) for f in files for line in open(f, encoding='utf-8')]


def test_real_llm_plans_and_burr_executes(client, operator, mocks, env):
    mocks.run('all_ok')
    assert operator.mode('llm').accepted
    response = operator.instruct(GOAL)
    assert response.accepted, response.reason
    final = client.wait_final(response.burr_app_id, timeout=300)
    files, records = _decisions(env)
    summary = [(r['decision'], [s.get('task') or s.get('block') for s in r['steps']],
                len(r['attempts'])) for r in records]
    assert final.state == MissionStatus.SUCCEEDED, (final.message, summary)
    assert all(r['decision'] != 'invalid' for r in records), summary
    assert 'goal received' in mocks.text()                 # the packages were really used
    print('\nreal LLM decisions:', summary)


def test_decision_replay_with_the_real_llm_is_stable(env):
    files, records = _decisions(env)
    assert records
    deviations = []
    for f in files:
        deviations += decision_replay.replay_decisions(f, LLMClient().chat, runs=2)
    assert deviations == []
