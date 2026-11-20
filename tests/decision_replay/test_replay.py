"""Decision replay must pass for an unchanged run and report changed decisions as failures."""

import asyncio
import json
import os
import shutil
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import replay as rp  # noqa: E402

rp._import_task_manager()

from georg_task_manager.burr_app.builder import make_tracker, PROJECT  # noqa: E402, I100
from georg_task_manager.burr_app.service import TaskManagerService  # noqa: E402
from georg_task_manager.mission_selector import get_mission  # noqa: E402


def record_run(storage, results):
    """Run digital_festival with the given task results and record it for the Burr UI."""
    os.environ['GEORG_BURR_TRACKING'] = '1'
    queue = list(results)

    async def scripted(task):
        return queue.pop(0) if queue else True

    service = TaskManagerService(run_task=scripted, tracker=make_tracker(str(storage)),
                                 log=lambda line: None)
    result = asyncio.run(service.run_mission('digital_festival', get_mission('digital_festival')))
    return os.path.join(str(storage), PROJECT, result.burr_app_id)


@pytest.fixture
def recorded(tmp_path):
    # doorbell fails twice (HIGH -> retried), one gesture fails (LOW -> discarded)
    return record_run(tmp_path, [False, False, True, False])


def test_recording_is_read(recorded):
    rec = rp.load_recording(recorded)
    assert rec.mission_id == 'digital_festival'
    assert rec.steps[:4] == ['start_mission', 'listen_doorbell', 'listen_doorbell',
                             'listen_doorbell']
    assert rec.results[:4] == [False, False, True, False]
    assert rec.outcome == 'succeeded'


def test_unchanged_run_replays_without_deviation(recorded):
    assert rp.replay(recorded, runs=3) == []
    assert rp.main([os.path.basename(recorded), '--storage',
                    os.path.dirname(os.path.dirname(recorded)), '--runs', '2']) == 0


def test_changed_decision_is_reported(recorded, tmp_path):
    tampered = str(tmp_path / 'tampered')
    shutil.copytree(recorded, tampered)
    log = os.path.join(tampered, 'log.jsonl')
    lines = open(log, encoding='utf-8').read().splitlines()
    for i, line in enumerate(lines):
        entry = json.loads(line)
        if entry.get('type') == 'end_entry' and entry['action'] == 'gesture_point_to':
            entry['state']['decision'] = 'ok | -> finish'      # pretend it stopped here
            lines[i] = json.dumps(entry)
            break
    open(log, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    deviations = rp.replay(tampered, runs=1)
    assert deviations and 'decision' in deviations[0]


def test_changed_rules_are_reported(recorded):
    # same recording, but the mission now behaves differently (e.g. after a code change)
    def other_mission(mission_id):
        tasks = get_mission(mission_id)
        return tasks[:-1]                                      # ReturnToIdle removed
    deviations = rp.replay(recorded, runs=1, mission_factory=other_mission)
    assert any('step' in d for d in deviations)


def test_llm_decisions_replay_and_report_changes(tmp_path):
    from georg_task_manager.catalog import load_catalog
    from georg_task_manager.planner.planner import Planner

    answer = json.dumps({'decision': 'plan', 'steps': [{'block': 'greet_guest'}], 'reason': 'x'})
    log_dir = tmp_path / 'decisions'
    p = Planner(lambda m, schema=None: answer, load_catalog(), 'mock', 'scripted',
                log_dir=str(log_dir))
    p.decide(p.context('greet', [], [], places=['Door']))
    log = str(next(log_dir.iterdir()))
    assert rp.replay_decisions(log, lambda m, schema=None: answer, runs=2) == []
    other = json.dumps({'decision': 'abort', 'steps': [], 'reason': 'changed model'})
    deviations = rp.replay_decisions(log, lambda m, schema=None: other, runs=1)
    assert deviations and 'abort' in deviations[0]
