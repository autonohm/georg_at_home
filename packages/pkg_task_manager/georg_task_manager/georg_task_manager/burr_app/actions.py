"""Burr actions of the task manager.

Every task type of the catalog is its own Burr node (``listen``, ``gesture``,
``navigate_object``, ...). Between two tasks the ``next`` node decides which
task comes next. In the Burr UI the sequence reads exactly as it happened::

    start_mission -> next -> listen -> next -> gesture -> next -> ... -> finish -> idle

``next`` works one step at a time. Today it takes the next entry of the fixed
mission and applies the priority rules; from P6 an LLM planner can take its
place and decide after every task, based on the last result.

Python task objects are not put into the Burr state (the state is serialized
for the Burr UI). The state holds indices, names and arguments; the task
objects live in the ``MissionContext`` that is bound to the actions.

Priority rules (unchanged from ``task_manager.py``):

- LOW:      failure -> task is discarded, mission continues
- MID:      failure -> retried once, after the next task
- HIGH:     failure -> retried immediately, up to 3 times, then discarded
- CRITICAL: like HIGH, but the mission fails when the retries are used up
"""

from dataclasses import dataclass, field
from typing import Awaitable, Callable, Dict, List

from burr.core import State, action

from georg_task_manager.tasks.priority import MAX_RETRIES, TaskPriority

RUNNING = "running"
SUCCEEDED = "succeeded"
FAILED = "failed"
ABORTED = "aborted"
DONE = "finish"   # value of next_task when the mission is over


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


def task_name(task) -> str:
    return getattr(task, "name", type(task).__name__)


def _plain(value):
    """JSON-friendly value for the Burr UI."""
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, TaskPriority):
        return value.value
    return str(value)


def task_args(task, names: List[str]) -> dict:
    args = {n: _plain(getattr(task, n)) for n in names if hasattr(task, n)}
    args["priority"] = _plain(getattr(task, "priority", TaskPriority.LOW))
    return args


def apply_priority(priority: TaskPriority, attempts: int, index: int, queue: List[int]):
    """Return (outcome, new_queue, text) after a failed task.

    ``attempts`` is the number of failed attempts including this one.
    Same rules and same queue positions as ``TaskManager._handle_failure``.
    """
    max_retries = MAX_RETRIES.get(priority, 0)
    if attempts > max_retries:
        if priority == TaskPriority.CRITICAL:
            return FAILED, queue, "critical, out of retries"
        return RUNNING, queue, f"discarded ({priority.name})"
    if priority in (TaskPriority.HIGH, TaskPriority.CRITICAL):
        return RUNNING, [index] + queue, f"retry now (attempt {attempts}/{max_retries})"
    if priority == TaskPriority.MID:
        return RUNNING, queue[:1] + [index] + queue[1:], \
            f"retry after next task (attempt {attempts}/{max_retries})"
    return RUNNING, queue, f"discarded ({priority.name})"


@action(
    reads=[],
    writes=["mission_id", "planned", "queue", "attempts", "current", "current_task",
            "next_task", "task_args", "last_result", "pending", "step", "total_steps",
            "outcome", "message", "executed", "decision"],
)
def start_mission(state: State, ctx: MissionContext, mission_id: str) -> State:
    ctx.log("\n=== Mission Started ===\n")
    return state.update(
        mission_id=mission_id,
        # only for reference; ``next`` decides step by step
        planned=[f"{t}: {task_name(task)}" for t, task in zip(ctx.task_types, ctx.tasks)],
        queue=list(range(len(ctx.tasks))),
        attempts=[0] * len(ctx.tasks),
        current=-1,
        current_task="",
        next_task="",
        task_args={},
        last_result=None,
        pending=False,
        step=0,
        total_steps=len(ctx.tasks),
        outcome=RUNNING,
        message="",
        executed=[],
        decision="",
    )


@action(
    reads=["queue", "attempts", "current", "current_task", "last_result", "pending"],
    writes=["queue", "attempts", "current", "current_task", "next_task", "task_args",
            "pending", "outcome", "message", "decision"],
)
def next_step(state: State, ctx: MissionContext) -> State:
    """Decide the next task: evaluate the last result, then pick one task.

    Mission mode: next entry of the mission + priority rules.
    From P6 an LLM planner replaces this decision.
    """
    queue = list(state["queue"])
    attempts = list(state["attempts"])
    notes = []

    # 1. result of the task that just ran
    if state["pending"]:
        index = state["current"]
        if state["last_result"]:
            notes.append(f"{state['current_task']}: ok")
        else:
            attempts[index] += 1
            priority = getattr(ctx.tasks[index], "priority", TaskPriority.LOW)
            outcome, queue, what = apply_priority(priority, attempts[index], index, queue)
            notes.append(f"{state['current_task']}: failed, {what}")
            ctx.log(f"[TASK FAILED] {state['current_task']}: {what}")
            if outcome == FAILED:
                ctx.log("[MISSION FAILED]")
                return state.update(
                    queue=queue, attempts=attempts, pending=False, next_task=DONE,
                    outcome=FAILED, message=notes[-1], decision=" | ".join(notes + ["stop"]))

    # 2. abort from the operator
    if ctx.abort_requested():
        ctx.log("\n[MISSION ABORTED] Stopping before next task\n")
        return state.update(
            queue=queue, attempts=attempts, pending=False, next_task=DONE,
            outcome=ABORTED, message="aborted by operator",
            decision=" | ".join(notes + ["abort requested -> stop"]))

    # 3. nothing left
    if not queue:
        return state.update(
            queue=queue, attempts=attempts, pending=False, next_task=DONE,
            outcome=SUCCEEDED, message="mission complete",
            decision=" | ".join(notes + ["mission complete"]))

    # 4. next task
    index = queue.pop(0)
    task = ctx.tasks[index]
    kind = ctx.task_types[index]
    name = task_name(task)
    ctx.on_current_task(name)
    ctx.log(f"[TASK MANAGER] Running {name}")
    return state.update(
        queue=queue, attempts=attempts, pending=False, current=index, current_task=name,
        next_task=kind, task_args=task_args(task, ctx.arg_names.get(kind, [])),
        decision=" | ".join(notes + [f"next: {kind} {name}"]))


@action(reads=["current", "current_task", "task_args", "step", "executed"],
        writes=["last_result", "pending", "step", "executed", "message"])
async def run_task(state: State, ctx: MissionContext, task_type: str) -> State:
    """One node per catalog task type. Runs the task that ``next`` picked."""
    index = state["current"]
    task = ctx.tasks[index]
    if ctx.task_types[index] != task_type:   # graph and mission out of sync
        raise RuntimeError(f"node '{task_type}' got task of type '{ctx.task_types[index]}'")
    message = ""
    try:
        result = bool(await ctx.run_task(task))
    except Exception as exc:  # a crashing task counts as a failed task
        result = False
        message = f"{state['current_task']} raised {type(exc).__name__}: {exc}"
        ctx.log(f"[TASK ERROR] {message}")
    ctx.log(f"[TASK RESULT] {result}\n")
    return state.update(
        last_result=result,
        pending=True,
        step=state["step"] + 1,
        executed=state["executed"] + [state["current_task"]],
        message=message,
    )


@action(reads=["outcome"], writes=["current_task", "current", "next_task", "task_args"])
def finish(state: State, ctx: MissionContext) -> State:
    ctx.on_current_task("Idle")
    if state["outcome"] == SUCCEEDED:
        ctx.log("=== Mission Complete ===")
    return state.update(current_task="Idle", current=-1, next_task="", task_args={})


@action(reads=[], writes=[])
def idle(state: State) -> State:
    """Terminal step of one mission run: the task manager waits for the next mission."""
    return state
