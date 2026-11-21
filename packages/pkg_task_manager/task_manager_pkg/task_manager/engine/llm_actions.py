"""Burr actions of the LLM mode (plan P6), graph "star".

Decision 2026-11-20, see docs/OPEN_QUESTIONS.md.

    start_llm -> next -> <task or block node> -> next -> ... -> finish -> idle

``next`` asks the planner after every task: continue, new plan, done or abort.
There is one node per catalog task (listen, gesture, ...) and one per mission block
(greet_guest, ...). A block node runs the block as its own Burr run with the fixed
chain of the block (like a mission), linked to this run as spawned child, so the Burr UI
shows it nested under the step that started it.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Awaitable, Callable, List, Optional
import uuid

from burr.core import action, ApplicationContext, State
from task_manager.catalog import Catalog
from task_manager.catalog.validator import block_tasks, instantiate
from task_manager.engine import actions as a
from task_manager.planner.llm_client import LLMError
from task_manager.planner.planner import Planner

MAX_TASK_RUNS = 30


@dataclass
class LLMContext:
    planner: Planner
    catalog: Catalog
    run_task: Callable[[object], Awaitable[bool]]
    abort_requested: Callable[[], bool] = lambda: False
    on_current_task: Callable[[str], None] = lambda name: None
    log: Callable[[str], None] = print
    # LLM + approval mode: async (items, reason) -> bool; None = no approval needed
    approve: Optional[Callable[[List[dict], str], Awaitable[bool]]] = None
    # returns new operator feedback (and clears it), '' if none
    feedback: Callable[[], str] = lambda: ''
    robot: Callable[[], dict] = lambda: {}
    places: List[str] = field(default_factory=list)
    # called with a JSON-able dict whenever the plan changes (plan topic for Lichtblick)
    on_plan: Callable[[dict], None] = lambda plan: None
    tracker: object = None
    max_task_runs: int = MAX_TASK_RUNS


def _label(item: dict) -> str:
    if 'block' in item:
        return f"block {item['block']}"
    args = ', '.join(f'{k}={v}' for k, v in sorted(item.get('args', {}).items()))
    return f"{item['task']}({args})"


@action(reads=[], writes=['goal', 'history', 'remaining', 'current', 'next_node', 'outcome',
                          'message', 'decision', 'task_runs', 'executed', 'last_result'])
def start_llm(state: State, ctx: LLMContext, goal: str) -> State:
    ctx.log(f'\n=== LLM run started: {goal} ===\n')
    return state.update(goal=goal, history=[], remaining=[], current={}, next_node='',
                        outcome=a.RUNNING, message='', decision={}, task_runs=0, executed=[],
                        last_result=None)


@action(reads=['goal', 'history', 'remaining', 'task_runs'],
        writes=['remaining', 'current', 'next_node', 'outcome', 'message', 'decision'])
async def next_step(state: State, ctx: LLMContext) -> State:
    """Ask the planner what comes next (after every task), apply the guard rails."""
    def stop(outcome, message, decision=None):
        ctx.log(f'[LLM] {outcome}: {message}')
        ctx.on_plan({'goal': state['goal'], 'outcome': outcome, 'reason': message,
                     'remaining': [], 'history': state['history']})
        return state.update(outcome=outcome, message=message, next_node=a.FINISH,
                            current={}, remaining=[], decision=decision or {})

    if ctx.abort_requested():
        return stop(a.ABORTED, 'aborted by operator')
    if state['task_runs'] >= ctx.max_task_runs:
        return stop(a.FAILED, f'more than {ctx.max_task_runs} tasks, stopped')

    remaining = list(state['remaining'])
    context = ctx.planner.context(state['goal'], state['history'], remaining,
                                  feedback=ctx.feedback(), robot=ctx.robot(), places=ctx.places)
    try:
        result = await asyncio.to_thread(ctx.planner.decide, context)
    except LLMError as exc:
        return stop(a.FAILED, str(exc))
    record = result.record
    summary = {'decision': result.decision, 'reason': result.reason,
               'steps': [_label(i) for i in result.items],
               'attempts': len(record.get('attempts', [])),
               'prompt_version': record.get('prompt_version'), 'model': record.get('model')}

    if not result.valid:
        return stop(a.FAILED, f'planner: {result.reason}', summary)
    if result.decision == 'abort':
        return stop(a.ABORTED, f'planner aborted: {result.reason}', summary)
    if result.decision == 'done':
        return stop(a.SUCCEEDED, f'goal reached: {result.reason}', summary)
    if result.decision == 'plan':
        remaining = list(result.items)
        if ctx.approve is not None:
            ctx.on_plan({'goal': state['goal'], 'waiting_for_approval': True,
                         'remaining': [_label(i) for i in remaining],
                         'reason': result.reason, 'history': state['history']})
            if not await ctx.approve(remaining, result.reason):
                return stop(a.ABORTED, 'plan rejected by the operator', summary)
    if not remaining:
        return stop(a.SUCCEEDED, 'plan finished', summary)

    current = remaining.pop(0)
    node = current.get('block') or current['task']
    ctx.on_current_task(_label(current))
    ctx.on_plan({'goal': state['goal'], 'current': _label(current),
                 'remaining': [_label(i) for i in remaining], 'reason': result.reason,
                 'decision': result.decision, 'history': state['history']})
    return state.update(remaining=remaining, current=current, next_node=node,
                        outcome=a.RUNNING, message=result.reason, decision=summary)


def _after_task(state: State, ok: bool, label: str, kind: str, error: str = '') -> State:
    entry = {'step': label, 'kind': kind, 'result': 'ok' if ok else 'failed'}
    if error:
        entry['error'] = error
    return state.update(last_result=ok, history=state['history'] + [entry],
                        task_runs=state['task_runs'] + 1,
                        executed=state['executed'] + [label])


@action(reads=['current', 'history', 'task_runs', 'executed'],
        writes=['last_result', 'history', 'task_runs', 'executed'])
async def run_llm_task(state: State, ctx: LLMContext, task_type: str) -> State:
    """Node of one catalog task in LLM mode."""
    item = state['current']
    task = instantiate([(task_type, item.get('args', {}))], ctx.catalog)[0]
    try:
        ok = bool(await ctx.run_task(task))
        error = ''
    except Exception as exc:  # a crashing task counts as a failed task
        ok, error = False, f'{type(exc).__name__}: {exc}'
    ctx.log(f'[LLM TASK] {_label(item)} -> {"ok" if ok else "failed"}')
    return _after_task(state, ok, _label(item), 'task', error)


@action(reads=['current', 'history', 'task_runs', 'executed'],
        writes=['last_result', 'history', 'task_runs', 'executed', 'block_app_id'])
async def run_block(state: State, ctx: LLMContext, block_name: str,
                    __context: ApplicationContext) -> State:
    """Node of one mission block: runs the block as its own (linked) Burr run, a chain."""
    from task_manager.engine.builder import build_mission_app

    tasks = block_tasks(block_name, ctx.catalog)
    results = []

    async def run_and_remember(task):
        ok = bool(await ctx.run_task(task))
        results.append(ok)
        return ok

    types = [ctx.catalog.by_class(type(t)).name for t in tasks]
    sub = a.MissionContext(
        tasks=tasks, task_types=types,
        arg_names={n: list(s.args_schema) for n, s in ctx.catalog.tasks.items()},
        run_task=run_and_remember, abort_requested=ctx.abort_requested,
        on_current_task=ctx.on_current_task, log=ctx.log,
        node_names=a.make_node_names(tasks, types, {n: s.name_arg for n, s in
                                                    ctx.catalog.tasks.items()}))
    tracker = __context.tracker.copy() if __context.tracker is not None else None
    app_id = str(uuid.uuid4())
    parent = (__context.app_id, __context.sequence_id, __context.partition_key)
    app = build_mission_app(sub, f'block:{block_name}', app_id=app_id, tracker=tracker,
                            spawning_parent=parent)
    final = None
    async for _act, _res, sub_state in app.aiterate(halt_after=['idle'],
                                                    inputs={'mission_id': f'block:{block_name}'}):
        final = sub_state
    ok = final is not None and final['outcome'] == a.SUCCEEDED and all(results) \
        and len(results) == len(tasks)
    ctx.log(f'[LLM BLOCK] {block_name} -> {"ok" if ok else "failed"} ({results})')
    return _after_task(state, ok, f'block {block_name}', 'block').update(block_app_id=app_id)
