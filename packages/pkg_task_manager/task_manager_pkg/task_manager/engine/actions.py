"""Burr actions of the task manager.

The Burr graph is built per mission run: one node per mission step, named
after the catalog task and its ``name_arg`` argument. A number is only added
when the same step occurs twice. For the Digital Festival mission::

    start_mission -> listen_doorbell -> gesture_look_at -> gesture_point_to -> listen_speech
                  -> gesture_look_at_2 -> gesture_greet_person -> return_to_idle -> finish -> idle

Each task node runs its task and then decides where to go next (``go_to``):
the next step, itself again (retry), a step back (MID retry after the next
task) or ``finish``. The decision is written to the node's state
(``decision``), so the Burr UI shows the sequence and the reasons at a glance.

Python task objects are not put into the Burr state (the state is serialized
for the Burr UI). The state holds indices, names and arguments; the task
objects live in the ``MissionContext`` that is bound to the actions.

Priority rules (same as the previous loop):

- LOW:      failure -> task is discarded, mission continues
- MID:      failure -> retried once, after the next task
- HIGH:     failure -> retried immediately, up to 3 times, then discarded
- CRITICAL: like HIGH, but the mission fails when the retries are used up
"""

from dataclasses import dataclass, field
import re
from typing import Awaitable, Callable, Dict, List, Optional, Tuple

from burr.core import action, State
from task_manager.tasks.priority import MAX_RETRIES, TaskPriority

RUNNING = 'running'
SUCCEEDED = 'succeeded'
FAILED = 'failed'
ABORTED = 'aborted'
FINISH = 'finish'
RESERVED = {'start_mission', FINISH, 'idle'}


def _slug(value) -> str:
    return re.sub(r'[^a-z0-9]+', '_', str(value).lower()).strip('_')[:30]


def make_node_names(tasks: List[object], task_types: List[str],
                    name_args: Dict[str, str]) -> List[str]:
    """Readable, unique Burr node names, e.g. ``gesture_look_at``, ``gesture_look_at_2``."""
    names, used = [], set(RESERVED)
    for task, kind in zip(tasks, task_types):
        base = kind
        arg = name_args.get(kind)
        if arg:
            slug = _slug(getattr(task, arg, ''))
            if slug:
                base = f'{kind}_{slug}'
        name, count = base, 1
        while name in used:
            count += 1
            name = f'{base}_{count}'
        used.add(name)
        names.append(name)
    return names


@dataclass
class MissionContext:
    """Everything an action needs that is not serializable state."""

    tasks: List[object]
    # catalog name of every task, e.g. "listen" (same order as tasks)
    task_types: List[str]
    # argument names per catalog task, shown in the Burr UI
    arg_names: Dict[str, List[str]] = field(default_factory=dict)
    # runs one task and returns True on success
    run_task: Callable[[object], Awaitable[bool]] = None
    # True if the operator asked to abort
    abort_requested: Callable[[], bool] = lambda: False
    # called with the task name before a task starts, and with "Idle" at the end
    on_current_task: Callable[[str], None] = lambda name: None
    log: Callable[[str], None] = print
    # Burr node name per mission step (see make_node_names); same order as tasks
    node_names: List[str] = field(default_factory=list)

    def node(self, index: int) -> str:
        return self.node_names[index]

    def priority(self, index: int) -> TaskPriority:
        return getattr(self.tasks[index], 'priority', TaskPriority.LOW)


def task_name(task) -> str:
    return getattr(task, 'name', type(task).__name__)


def _plain(value):
    """JSON-friendly value for the Burr UI."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, TaskPriority):
        return value.value
    if callable(value):
        return '(text from the state at run time)'
    return str(value)


def task_args(task, names: List[str]) -> dict:
    args = {n: _plain(getattr(task, n)) for n in names if hasattr(task, n)}
    args['priority'] = _plain(getattr(task, 'priority', TaskPriority.LOW))
    return args


# --- decision logic, without Burr (also used to compute the graph edges) -------

def apply_priority(priority: TaskPriority, attempts: int, index: int, queue: List[int]):
    """Return (outcome, new_queue, text) after a failed task.

    ``attempts`` is the number of failed attempts including this one.
    Same rules and same queue positions as ``TaskManager._handle_failure``.
    """
    max_retries = MAX_RETRIES.get(priority, 0)
    if attempts > max_retries:
        if priority == TaskPriority.CRITICAL:
            return FAILED, queue, 'critical, out of retries'
        return RUNNING, queue, f'discarded ({priority.name})'
    if priority in (TaskPriority.HIGH, TaskPriority.CRITICAL):
        return RUNNING, [index] + queue, f'retry now (attempt {attempts}/{max_retries})'
    if priority == TaskPriority.MID:
        return RUNNING, queue[:1] + [index] + queue[1:], \
            f'retry after next task (attempt {attempts}/{max_retries})'
    return RUNNING, queue, f'discarded ({priority.name})'


def decide(queue: List[int], attempts: List[int], current: int, last_result: Optional[bool],
           priorities: List[TaskPriority], abort: bool
           ) -> Tuple[str, List[int], List[int], int, List[str]]:
    """Evaluate the last result (if any) and pick the next mission step.

    Returns (outcome, queue, attempts, next_index or -1, notes).
    Order of checks is the same as in ``TaskManager.run``: failure handling,
    then abort, then the next task.
    """
    queue, attempts, notes = list(queue), list(attempts), []
    if current >= 0:
        if last_result:
            notes.append('ok')
        else:
            attempts[current] += 1
            outcome, queue, what = apply_priority(
                priorities[current], attempts[current], current, queue)
            notes.append(f'failed, {what}')
            if outcome == FAILED:
                return FAILED, queue, attempts, -1, notes
    if abort:
        return ABORTED, queue, attempts, -1, notes + ['abort requested']
    if not queue:
        return SUCCEEDED, queue, attempts, -1, notes + ['mission complete']
    return RUNNING, queue[1:], attempts, queue[0], notes


def _apply_decision(state: State, ctx: MissionContext, current: int,
                    last_result: Optional[bool]) -> State:
    outcome, queue, attempts, nxt, notes = decide(
        state['queue'], state['attempts'], current, last_result,
        [ctx.priority(i) for i in range(len(ctx.tasks))], ctx.abort_requested())

    if current >= 0 and not last_result:
        ctx.log(f"[TASK FAILED] {task_name(ctx.tasks[current])}: {notes[0].split(', ', 1)[-1]}")
    if outcome == RUNNING:
        task = ctx.tasks[nxt]
        go_to = ctx.node(nxt)
        name = task_name(task)
        ctx.on_current_task(name)
        ctx.log(f'[TASK MANAGER] Running {name}')
        updates = {'current': nxt, 'next_task': name,
                   'next_args': task_args(task, ctx.arg_names.get(ctx.task_types[nxt], []))}
    else:
        go_to = FINISH
        if outcome == ABORTED:
            ctx.log('\n[MISSION ABORTED] Stopping before next task\n')
        if outcome == FAILED:
            ctx.log('[MISSION FAILED]')
        updates = {'current': -1, 'next_task': '', 'next_args': {}}

    return state.update(queue=queue, attempts=attempts, outcome=outcome, go_to=go_to,
                        decision=' | '.join(notes + [f'-> {go_to}']),
                        message=notes[-1] if notes else '', **updates)


# --- Burr actions --------------------------------------------------------------

DECISION_KEYS = ['queue', 'attempts', 'outcome', 'go_to', 'decision', 'message',
                 'current', 'next_task', 'next_args']


@action(reads=[], writes=['mission_id', 'planned', 'step', 'executed', 'task', 'args',
                          'last_result'] + DECISION_KEYS)
def start_mission(state: State, ctx: MissionContext, mission_id: str) -> State:
    ctx.log('\n=== Mission Started ===\n')
    state = state.update(
        mission_id=mission_id,
        planned=[ctx.node(i) for i in range(len(ctx.tasks))],
        queue=list(range(len(ctx.tasks))),
        attempts=[0] * len(ctx.tasks),
        step=0,
        executed=[],
        task='',
        args={},
        last_result=None,
    )
    return _apply_decision(state, ctx, current=-1, last_result=None)


@action(reads=['current', 'next_task', 'next_args', 'queue', 'attempts', 'step', 'executed'],
        writes=['task', 'args', 'last_result', 'step', 'executed'] + DECISION_KEYS)
async def run_task(state: State, ctx: MissionContext, index: int) -> State:
    """Node of one mission step: run the task, then decide where to go next."""
    if state['current'] != index:   # graph and decision out of sync
        raise RuntimeError(f"node {ctx.node(index)} reached, but step {state['current']} is due")
    task = ctx.tasks[index]
    name, args = state['next_task'], state['next_args']
    error = ''
    try:
        result = bool(await ctx.run_task(task))
    except Exception as exc:  # a crashing task counts as a failed task
        result = False
        error = f'{name} raised {type(exc).__name__}: {exc}'
        ctx.log(f'[TASK ERROR] {error}')
    ctx.log(f'[TASK RESULT] {result}\n')
    state = state.update(task=name, args=args, last_result=result,
                         step=state['step'] + 1, executed=state['executed'] + [name])
    state = _apply_decision(state, ctx, current=index, last_result=result)
    if error:
        state = state.update(message=error)
    return state


@action(reads=['outcome'], writes=['current_task'])
def finish(state: State, ctx: MissionContext) -> State:
    ctx.on_current_task('Idle')
    if state['outcome'] == SUCCEEDED:
        ctx.log('=== Mission Complete ===')
    return state.update(current_task='Idle')


@action(reads=[], writes=[])
def idle(state: State) -> State:
    """Terminal step of one mission run: the task manager waits for the next mission."""
    return state
