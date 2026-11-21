"""LLM planner and LLM mode (P6) with a scripted LLM: guard rails, feedback loop, logging."""

import asyncio
import json
import os

from georg_task_manager.catalog import load_catalog
from georg_task_manager.engine.builder import make_tracker, PROJECT
from georg_task_manager.engine.service import TaskManagerService
from georg_task_manager.planner import prompts
from georg_task_manager.planner.planner import Planner
import pytest


class ScriptedLLM:
    """Answers from a list, one per call; records what it was asked."""

    def __init__(self, answers):
        self.answers = [a if isinstance(a, str) else json.dumps(a) for a in answers]
        self.calls = []

    def __call__(self, messages, schema=None):
        self.calls.append(list(messages))
        if not self.answers:
            return json.dumps({'decision': 'abort', 'steps': [], 'reason': 'script empty'})
        return self.answers.pop(0)

    def context(self, call):
        return json.loads(self.calls[call][1]['content'])


def plan(*steps, reason='ok'):
    return {'decision': 'plan', 'steps': list(steps), 'reason': reason}


def say(decision, reason='ok'):
    return {'decision': decision, 'steps': [], 'reason': reason}


GESTURE = {'task': 'gesture', 'args': {'mode': 'look_at', 'vx': -1000.0, 'vy': 0.0, 'vz': 100.0}}


@pytest.fixture
def catalog():
    return load_catalog()


def planner(llm, catalog, tmp_path, **kw):
    return Planner(llm, catalog, mode='mock', model='scripted',
                   log_dir=str(tmp_path / 'log'), **kw)


# --- planner ------------------------------------------------------------------

def test_valid_plan_is_accepted_and_logged(catalog, tmp_path):
    llm = ScriptedLLM([plan({'block': 'wait_for_guest'}, GESTURE)])
    p = planner(llm, catalog, tmp_path)
    result = p.decide(p.context('greet the guest', [], []))
    assert result.decision == 'plan'
    assert result.items == [{'block': 'wait_for_guest'}, GESTURE]
    logged = [json.loads(line) for line in
              open(next((tmp_path / 'log').iterdir()), encoding='utf-8')]
    assert logged[0]['prompt_version'] == prompts.PROMPT_VERSION
    assert logged[0]['model'] == 'scripted'
    assert logged[0]['input']['goal'] == 'greet the guest'
    assert logged[0]['decision'] == 'plan' and len(logged[0]['attempts']) == 1


def test_context_has_catalog_but_no_file_paths(catalog, tmp_path):
    p = planner(ScriptedLLM([]), catalog, tmp_path)
    ctx = p.context('goal', [], [], places=['Seat'])
    assert 'navigate_object' in ctx['available']['tasks']
    assert 'map_path' not in ctx['available']['tasks']['navigate_object']['args']
    assert 'greet_guest' in ctx['available']['blocks']
    assert ctx['places'] == ['Seat']


def test_invalid_answer_goes_back_with_error_text(catalog, tmp_path):
    llm = ScriptedLLM(['not json', plan({'task': 'fly'}), plan(GESTURE)])
    p = planner(llm, catalog, tmp_path)
    result = p.decide(p.context('goal', [], []))
    assert result.decision == 'plan' and len(result.record['attempts']) == 3
    second, third = llm.calls[1][-1]['content'], llm.calls[2][-1]['content']
    assert 'rejected' in second and 'invalid JSON' in second
    assert "unknown task 'fly'" in third


def test_gives_up_after_the_attempt_limit(catalog, tmp_path):
    llm = ScriptedLLM([plan({'task': 'fly'})] * 5)
    p = planner(llm, catalog, tmp_path, max_attempts=3)
    result = p.decide(p.context('goal', [], []))
    assert result.decision == 'invalid' and len(llm.calls) == 3
    assert 'no valid plan after 3 attempts' in result.reason


@pytest.mark.parametrize('answer, error', [
    ({'decision': 'maybe'}, 'decision must be one of'),
    ({'decision': 'done', 'steps': [GESTURE]}, 'takes no steps'),
    (plan(*[GESTURE] * 9), 'maximum is 8'),
    (plan({'task': 'gesture', 'args': {'mode': 'dance', 'vx': 0, 'vy': 0, 'vz': 0}}), 'not in'),
])
def test_guard_rails(catalog, tmp_path, answer, error):
    p = planner(ScriptedLLM([]), catalog, tmp_path)
    assert any(error in e for e in p.check(answer)), p.check(answer)


# --- LLM mode in Burr ---------------------------------------------------------

def run_llm(catalog, tmp_path, answers, results=None, approve=None, tracker=None,
            abort_at=None):
    llm = ScriptedLLM(answers)
    queue = list(results or [])
    svc = None

    async def run_task(task):
        if abort_at is not None and len(queue) == abort_at:
            svc.request_abort()
            return False
        return queue.pop(0) if queue else True

    svc = TaskManagerService(run_task=run_task, catalog=catalog, tracker=tracker,
                             log=lambda line: None)
    p = planner(llm, catalog, tmp_path)
    result = asyncio.run(svc.run_llm('greet the guest', p, approve=approve))
    return result, llm


def test_llm_plans_and_burr_executes_without_intervention(catalog, tmp_path):
    result, llm = run_llm(catalog, tmp_path, [
        plan({'block': 'wait_for_guest'}, GESTURE), say('continue'), say('done')])
    assert result.outcome == 'succeeded'
    assert result.steps == ['start_llm', 'next', 'wait_for_guest', 'next', 'gesture',
                            'next', 'finish', 'idle']
    # after every task the result goes back to the LLM
    assert llm.context(1)['history'] == [{'step': 'block wait_for_guest', 'kind': 'block',
                                          'result': 'ok'}]
    assert len(llm.context(2)['history']) == 2


def test_invalid_plans_end_in_idle(catalog, tmp_path):
    result, llm = run_llm(catalog, tmp_path, [plan({'task': 'fly'})] * 3)
    assert result.outcome == 'failed'
    assert 'no valid plan after 3 attempts' in result.message
    assert result.steps == ['start_llm', 'next', 'finish', 'idle']


def test_failed_task_leads_to_replan(catalog, tmp_path):
    result, llm = run_llm(catalog, tmp_path, [
        plan(GESTURE), plan({'block': 'greet_guest'}, reason='gesture failed, try block'),
        say('done')], results=[False])
    assert result.outcome == 'succeeded'
    assert llm.context(1)['history'][0]['result'] == 'failed'
    assert result.steps[:6] == ['start_llm', 'next', 'gesture', 'next', 'greet_guest', 'next']


def test_failed_task_leads_to_clean_abort(catalog, tmp_path):
    result, _ = run_llm(catalog, tmp_path, [plan(GESTURE), say('abort', 'cannot greet')],
                        results=[False])
    assert result.outcome == 'aborted'
    assert 'cannot greet' in result.message


def test_plan_needs_approval_in_approval_mode(catalog, tmp_path):
    asked = []

    async def reject(items, reason):
        asked.append(items)
        return False

    result, _ = run_llm(catalog, tmp_path, [plan(GESTURE)], approve=reject)
    assert asked == [[GESTURE]]
    assert result.outcome == 'aborted' and 'rejected' in result.message
    assert 'gesture' not in result.steps


def test_operator_abort_during_llm_run(catalog, tmp_path):
    result, _ = run_llm(catalog, tmp_path, [plan(GESTURE, GESTURE)], abort_at=0)
    assert result.outcome == 'aborted'
    assert result.steps.count('gesture') == 1


def test_block_runs_as_linked_child_in_the_burr_ui(catalog, tmp_path, monkeypatch):
    monkeypatch.setenv('GEORG_BURR_TRACKING', '1')
    tracker = make_tracker(str(tmp_path / 'burr'))
    result, _ = run_llm(catalog, tmp_path, [plan({'block': 'greet_guest'}), say('done')],
                        tracker=tracker)
    project = tmp_path / 'burr' / PROJECT
    children = [d for d in project.iterdir() if d.name != result.burr_app_id]
    assert len(children) == 1
    meta = json.loads((children[0] / 'metadata.json').read_text())
    assert meta['spawning_parent_pointer']['app_id'] == result.burr_app_id
    steps = [json.loads(line)['action'] for line in
             (children[0] / 'log.jsonl').read_text().splitlines()
             if json.loads(line).get('type') == 'end_entry']
    assert steps == ['start_mission', 'gesture_look_at', 'gesture_point_to',
                     'gesture_greet_person', 'finish', 'idle']
    assert os.path.exists(project / result.burr_app_id / 'graph.json')


def test_continue_without_plan_and_unknown_places_are_rejected(catalog, tmp_path):
    p = planner(ScriptedLLM([]), catalog, tmp_path)
    ctx = p.context('goal', [], [], places=['Door', 'Seat'])
    assert 'nothing to continue' in p.check(say('continue'), ctx)[0]
    nav = {'task': 'navigate_object', 'args': {'object_name': 'Moon'}}
    assert "unknown place 'Moon'" in p.check(plan(nav), ctx)[0]
    assert p.check(plan({'task': 'navigate_object', 'args': {'object_name': 'Seat'}}), ctx) == []


def test_schema_limits_names_and_places(catalog):
    schema = prompts.answer_schema(catalog, 'mock', 8, places=['Door', 'Seat'])
    plan_schema = schema['oneOf'][0]['properties']['steps']['items']['anyOf']
    names = [s['properties'].get('task', s['properties'].get('block'))['const']
             for s in plan_schema]
    assert set(names) == set(catalog.tasks) | set(catalog.blocks)
    nav = next(s for s in plan_schema if s['properties'].get('task', {}).get('const')
               == 'navigate_object')
    assert nav['properties']['args']['properties']['object_name']['enum'] == ['Door', 'Seat']
    assert 'map_path' not in nav['properties']['args']['properties']
