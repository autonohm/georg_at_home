"""Builds the Burr application for one mission run.

The graph is built from the mission itself: one node per mission step
(``listen_doorbell``, ``gesture_look_at``, ...). Only transitions that the priority rules
can actually produce are added, so a mission reads as a straight line with
a few extra arrows::

    start_mission -> listen_doorbell -> gesture_look_at -> ... -> finish -> idle
                       ^          |
                       +----------+   retry (HIGH / CRITICAL)

Every node also has an arrow to ``finish`` (abort, CRITICAL failure, done).
Every run gets its own ``app_id`` and therefore its own entry in the Burr UI
(project ``georg_task_manager``, partition key = mission id).
"""

import os
import uuid
from collections import deque
from typing import List, Optional, Set, Tuple

from burr.core import ApplicationBuilder, when

from georg_task_manager.burr_app import actions as a
from georg_task_manager.tasks.priority import TaskPriority

PROJECT = "georg_task_manager"
START = "start_mission"
MAX_EXPLORED = 200_000


def make_tracker(storage_dir: Optional[str] = None):
    """Local Burr tracker, or None if tracking is switched off.

    GEORG_BURR_TRACKING=0 switches it off.
    GEORG_BURR_STORAGE_DIR (default ~/.burr) is the folder the Burr UI reads.
    """
    if os.environ.get("GEORG_BURR_TRACKING", "1") == "0":
        return None
    from burr.tracking import LocalTrackingClient

    storage_dir = storage_dir or os.environ.get("GEORG_BURR_STORAGE_DIR", "~/.burr")
    return LocalTrackingClient(project=PROJECT, storage_dir=storage_dir)


def possible_edges(priorities: List[TaskPriority]) -> Set[Tuple[int, int]]:
    """All (from, to) step transitions the priority rules can produce.

    Step -1 is ``start_mission``, step -2 is ``finish``. Explores every
    combination of success and failure with the same ``decide`` function the
    actions use, so the graph and the run can never disagree.
    """
    n = len(priorities)
    edges: Set[Tuple[int, int]] = set()
    start = (tuple(range(n)), tuple([0] * n), -1)
    seen, todo = {start}, deque([start])
    while todo:
        if len(seen) > MAX_EXPLORED:
            raise RuntimeError("mission too complex to draw; split it into smaller missions")
        queue, attempts, current = todo.popleft()
        results = [None] if current < 0 else [True, False]
        for result in results:
            for abort in (False, True):
                outcome, q, att, nxt, _ = a.decide(
                    list(queue), list(attempts), current, result, priorities, abort)
                if outcome != a.RUNNING:
                    edges.add((current, -2))
                    continue
                edges.add((current, nxt))
                key = (tuple(q), tuple(att), nxt)
                if key not in seen:
                    seen.add(key)
                    todo.append(key)
    return edges


def build_mission_app(ctx: a.MissionContext, mission_id: str,
                      app_id: Optional[str] = None, tracker=None):
    def name(step: int) -> str:
        return {-1: START, -2: a.FINISH}.get(step) or ctx.node(step)

    priorities = [ctx.priority(i) for i in range(len(ctx.tasks))]
    edges = sorted(possible_edges(priorities))
    task_nodes = {ctx.node(i): a.run_task.bind(ctx=ctx, index=i) for i in range(len(ctx.tasks))}

    transitions = [(name(src), name(dst), when(go_to=name(dst))) for src, dst in edges]
    transitions.append((a.FINISH, "idle"))

    builder = (
        ApplicationBuilder()
        .with_actions(
            start_mission=a.start_mission.bind(ctx=ctx),
            finish=a.finish.bind(ctx=ctx),
            idle=a.idle,
            **task_nodes,
        )
        .with_transitions(*transitions)
        .with_entrypoint(START)
        .with_identifiers(app_id=app_id or str(uuid.uuid4()), partition_key=mission_id)
    )
    if tracker is not None:
        builder = builder.with_tracker(tracker)
    return builder.build()
