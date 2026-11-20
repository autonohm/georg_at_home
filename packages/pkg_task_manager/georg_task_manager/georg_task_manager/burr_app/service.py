"""Long-running task manager service: Idle -> Mission -> Idle, without restart.

No ROS in here. The ROS side (``ros_adapter.py`` now, ``ros_bridge.py`` in P2)
only passes in how a task is run and how the current task is published.
"""

import asyncio
import threading
import uuid
from dataclasses import dataclass, field
from typing import Awaitable, Callable, List, Optional

from georg_task_manager.burr_app import actions as a
from georg_task_manager.burr_app.builder import build_mission_app, make_tracker
from georg_task_manager.catalog import load_catalog
from georg_task_manager.validator import check_mission

IDLE = "idle"


@dataclass
class MissionResult:
    accepted: bool
    outcome: str = ""          # succeeded | failed | aborted ("" if not accepted)
    reason: str = ""
    burr_app_id: str = ""
    executed: List[str] = field(default_factory=list)
    message: str = ""


class TaskManagerService:

    def __init__(self, run_task: Callable[[object], Awaitable[bool]],
                 on_current_task: Callable[[str], None] = lambda name: None,
                 on_step: Callable[[str, dict], None] = lambda action, state: None,
                 catalog=None, tracker="default", log: Callable[[str], None] = print):
        self._run_task = run_task
        self._on_current_task = on_current_task
        self._on_step = on_step
        self._catalog = catalog if catalog is not None else load_catalog()
        self._tracker = make_tracker() if tracker == "default" else tracker
        self._log = log
        self._abort = threading.Event()
        self._lock = threading.Lock()
        self._running = False
        self.state = IDLE
        self.current_app_id = ""

    @property
    def running(self) -> bool:
        return self._running

    def request_abort(self) -> bool:
        """Abort the running mission. Returns False if nothing is running."""
        if not self._running:
            return False
        self._abort.set()
        return True

    @property
    def abort_requested(self) -> bool:
        return self._abort.is_set()

    async def run_mission(self, mission_id: str, tasks: List[object],
                          app_id: Optional[str] = None) -> MissionResult:
        with self._lock:
            if self._running:
                return MissionResult(
                    False, reason=f"mission '{self.current_app_id}' is still running")
            errors = check_mission(tasks, self._catalog)
            if errors:
                return MissionResult(False, reason="; ".join(errors))
            self._running = True
            self._abort.clear()
            self.current_app_id = app_id or str(uuid.uuid4())

        ctx = a.MissionContext(
            tasks=list(tasks),
            run_task=self._run_task,
            abort_requested=self._abort.is_set,
            on_current_task=self._on_current_task,
            log=self._log,
        )
        app = build_mission_app(ctx, mission_id, app_id=self.current_app_id, tracker=self._tracker)
        self.state = a.RUNNING
        final = None
        try:
            async for act, _result, state in app.aiterate(
                    halt_after=["idle"], inputs={"mission_id": mission_id}):
                final = state
                self._on_step(act.name, state.get_all())
        finally:
            with self._lock:
                self._running = False
                self.state = IDLE

        return MissionResult(
            True,
            outcome=final["outcome"],
            burr_app_id=self.current_app_id,
            executed=list(final["executed"]),
            message=final["message"],
        )

    def run_mission_blocking(self, mission_id: str, tasks: List[object]) -> MissionResult:
        return asyncio.run(self.run_mission(mission_id, tasks))
