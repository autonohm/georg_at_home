"""Burr actions of the task manager.

The actions replace the loop in ``task_manager.py`` (and the py_trees tick
loop) one to one. Tasks and missions stay exactly as before: a mission is a
list of ``BaseTask`` objects, each with a priority.

Python task objects are not put into the Burr state, because the state is
serialized for the Burr UI. The state only holds indices and names; the task
objects live in the ``MissionContext`` that is bound to the actions.

Priority rules (unchanged from ``task_manager.py``):

- LOW:      failure -> task is discarded, mission continues
- MID:      failure -> retried once, after the next task
- HIGH:     failure -> retried immediately, up to 3 times, then discarded
- CRITICAL: like HIGH, but the mission fails when the retries are used up
"""

from dataclasses import dataclass, field
from typing import Awaitable, Callable, List

from burr.core import State, action

from georg_task_manager.tasks.priority import MAX_RETRIES, TaskPriority

RUNNING = "running"
SUCCEEDED = "succeeded"
FAILED = "failed"
ABORTED = "aborted"


@dataclass
class MissionContext:
    """Everything an action needs that is not serializable state."""

    tasks: List[object]
    # runs one task and returns True on success
    run_task: Callable[[object], Awaitable[bool]]
    # True if the operator asked to abort
    abort_requested: Callable[[], bool] = lambda: False
    # called with the task name before a task starts, and with "Idle" at the end
    on_current_task: Callable[[str], None] = lambda name: None
    log: Callable[[str], None] = print
    extra: dict = field(default_factory=dict)


def _task_name(task) -> str:
    return getattr(task, "name", type(task).__name__)


@action(
    reads=[],
    writes=["mission_id", "task_names", "queue", "attempts", "current", "current_task",
            "step", "total_steps", "last_result", "outcome", "message", "executed"],
)
def start_mission(state: State, ctx: MissionContext, mission_id: str) -> State:
    names = [_task_name(t) for t in ctx.tasks]
    ctx.log("\n=== Mission Started ===\n")
    return state.update(
        mission_id=mission_id,
        task_names=names,
        queue=list(range(len(ctx.tasks))),
        attempts=[0] * len(ctx.tasks),
        current=-1,
        current_task="",
        step=0,
        total_steps=len(ctx.tasks),
        last_result=None,
        outcome=RUNNING,
        message="",
        executed=[],
    )


@action(reads=["queue", "task_names", "outcome"],
        writes=["queue", "current", "current_task", "outcome", "message"])
def select_task(state: State, ctx: MissionContext) -> State:
    if ctx.abort_requested():
        ctx.log("\n[MISSION ABORTED] Stopping before next task\n")
        return state.update(outcome=ABORTED, message="aborted by operator", current=-1)

    queue = list(state["queue"])
    if not queue:
        return state.update(outcome=SUCCEEDED, message="mission complete", current=-1)

    index = queue.pop(0)
    name = state["task_names"][index]
    ctx.on_current_task(name)
    ctx.log(f"[TASK MANAGER] Running {name}")
    return state.update(queue=queue, current=index, current_task=name)


@action(reads=["current", "step", "executed", "task_names"],
        writes=["last_result", "step", "executed", "message"])
async def run_task(state: State, ctx: MissionContext) -> State:
    index = state["current"]
    task = ctx.tasks[index]
    message = ""
    try:
        result = bool(await ctx.run_task(task))
    except Exception as exc:  # a crashing task counts as a failed task
        result = False
        message = f"{state['task_names'][index]} raised {type(exc).__name__}: {exc}"
        ctx.log(f"[TASK ERROR] {message}")
    ctx.log(f"[TASK RESULT] {result}\n")
    return state.update(
        last_result=result,
        step=state["step"] + 1,
        executed=state["executed"] + [state["task_names"][index]],
        message=message,
    )


def apply_priority(priority: TaskPriority, attempts: int, index: int, queue: List[int]):
    """Return (outcome, new_queue, log_line) after a failed task.

    ``attempts`` is the number of failed attempts including this one.
    Same rules and same queue positions as ``TaskManager._handle_failure``.
    """
    max_retries = MAX_RETRIES.get(priority, 0)
    name_hint = priority.name
    if attempts > max_retries:
        if priority == TaskPriority.CRITICAL:
            return FAILED, queue, "critical, out of retries"
        return RUNNING, queue, f"discarded ({name_hint})"
    if priority in (TaskPriority.HIGH, TaskPriority.CRITICAL):
        return RUNNING, [index] + queue, f"retries immediately (attempt {attempts}/{max_retries})"
    if priority == TaskPriority.MID:
        return RUNNING, queue[:1] + [index] + queue[1:], \
            f"retries after next task (attempt {attempts}/{max_retries})"
    return RUNNING, queue, f"discarded ({name_hint})"


@action(reads=["last_result", "current", "queue", "attempts", "task_names"],
        writes=["queue", "attempts", "outcome", "message"])
def handle_result(state: State, ctx: MissionContext) -> State:
    if state["last_result"]:
        return state.update(outcome=RUNNING)

    index = state["current"]
    task = ctx.tasks[index]
    name = state["task_names"][index]
    attempts = list(state["attempts"])
    attempts[index] += 1
    priority = getattr(task, "priority", TaskPriority.LOW)

    outcome, queue, what = apply_priority(priority, attempts[index], index, list(state["queue"]))
    ctx.log(f"[TASK FAILED] {name}: {what}")
    message = f"{name}: {what}"
    if outcome == FAILED:
        ctx.log("[MISSION FAILED]")
    return state.update(queue=queue, attempts=attempts, outcome=outcome, message=message)


@action(reads=["outcome", "message"], writes=["current_task", "current"])
def finish(state: State, ctx: MissionContext) -> State:
    ctx.on_current_task("Idle")
    if state["outcome"] == SUCCEEDED:
        ctx.log("=== Mission Complete ===")
    return state.update(current_task="Idle", current=-1)


@action(reads=[], writes=[])
def idle(state: State) -> State:
    """Terminal step of one mission run: the task manager waits for the next mission."""
    return state
