"""Builds the Burr application for one mission run.

One node per catalog task type, generated from ``catalog.yaml``. ``next``
decides after every task which node runs next::

                 +--> listen ----------+
    start_mission -> next --> gesture ---------+--> next ...
                 +--> navigate_object -+
                 +--> return_to_idle --+
                 +--> finish -> idle   (complete, failed or aborted)

Every run gets its own ``app_id`` and therefore its own entry in the Burr UI
(project ``georg_task_manager``, partition key = mission id).
"""

import os
import uuid
from typing import Optional

from burr.core import ApplicationBuilder, default, when

from georg_task_manager.burr_app import actions as a
from georg_task_manager.catalog import Catalog

PROJECT = "georg_task_manager"
RESERVED = {"start_mission", "next", "finish", "idle"}


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


def build_mission_app(ctx: a.MissionContext, mission_id: str, catalog: Catalog,
                      app_id: Optional[str] = None, tracker=None):
    clash = RESERVED & set(catalog.tasks)
    if clash:
        raise ValueError(f"catalog task names {sorted(clash)} are reserved Burr nodes")

    task_nodes = {name: a.run_task.bind(ctx=ctx, task_type=name) for name in catalog.tasks}
    transitions = [("start_mission", "next")]
    transitions += [("next", name, when(next_task=name)) for name in task_nodes]
    transitions += [("next", "finish", default)]
    transitions += [(name, "next") for name in task_nodes]
    transitions += [("finish", "idle")]

    builder = (
        ApplicationBuilder()
        .with_actions(
            start_mission=a.start_mission.bind(ctx=ctx),
            next=a.next_step.bind(ctx=ctx),
            finish=a.finish.bind(ctx=ctx),
            idle=a.idle,
            **task_nodes,
        )
        .with_transitions(*transitions)
        .with_entrypoint("start_mission")
        .with_identifiers(app_id=app_id or str(uuid.uuid4()), partition_key=mission_id)
    )
    if tracker is not None:
        builder = builder.with_tracker(tracker)
    return builder.build()
