"""Builds the Burr application for one mission run.

Graph (one run per mission, the service stays alive in between)::

    start_mission -> select_task -> run_task -> handle_result -+-> select_task ...
                          |                          |
                          +-------- finish <---------+   (done, failed or aborted)
                                      |
                                     idle

Every run gets its own ``app_id`` and therefore its own entry in the Burr UI
(project ``georg_task_manager``, partition key = mission id).
"""

import os
import uuid
from typing import Optional

from burr.core import ApplicationBuilder, default, when

from georg_task_manager.burr_app import actions as a

PROJECT = "georg_task_manager"


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


def build_mission_app(ctx: a.MissionContext, mission_id: str,
                      app_id: Optional[str] = None, tracker=None):
    app_id = app_id or str(uuid.uuid4())
    builder = (
        ApplicationBuilder()
        .with_actions(
            start_mission=a.start_mission.bind(ctx=ctx),
            select_task=a.select_task.bind(ctx=ctx),
            run_task=a.run_task.bind(ctx=ctx),
            handle_result=a.handle_result.bind(ctx=ctx),
            finish=a.finish.bind(ctx=ctx),
            idle=a.idle,
        )
        .with_transitions(
            ("start_mission", "select_task"),
            ("select_task", "run_task", when(outcome=a.RUNNING)),
            ("select_task", "finish", default),
            ("run_task", "handle_result"),
            ("handle_result", "select_task", when(outcome=a.RUNNING)),
            ("handle_result", "finish", default),
            ("finish", "idle"),
        )
        .with_entrypoint("start_mission")
        .with_identifiers(app_id=app_id, partition_key=mission_id)
    )
    if tracker is not None:
        builder = builder.with_tracker(tracker)
    return builder.build()
