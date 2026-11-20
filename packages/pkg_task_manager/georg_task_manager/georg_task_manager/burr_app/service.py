"""Long-running task manager service: Idle -> Mission -> Idle, without restart.

No ROS in here. The ROS side (``ros_adapter.py`` now, ``ros_bridge.py`` in P2)
only passes in how a task is run and how the current task is published.
"""

import asyncio
from dataclasses import dataclass, field
import threading
from typing import Awaitable, Callable, List, Optional
import uuid

from georg_task_manager.burr_app import actions as a
from georg_task_manager.burr_app.builder import build_mission_app, make_tracker
from georg_task_manager.catalog import load_catalog
from georg_task_manager.validator import check_mission

IDLE = 'idle'


@dataclass
class MissionResult:
    accepted: bool
    outcome: str = ''          # succeeded | failed | aborted ("" if not accepted)
    reason: str = ''
    burr_app_id: str = ''
    executed: List[str] = field(default_factory=list)
    # Burr nodes in the order they ran, e.g. start_mission, listen_doorbell, gesture_look_at, ...
    steps: List[str] = field(default_factory=list)
    message: str = ''


class TaskManagerService:

    def __init__(self, run_task: Callable[[object], Awaitable[bool]],
                 on_current_task: Callable[[str], None] = lambda name: None,
                 on_step: Callable[[str, dict], None] = lambda action, state: None,
                 catalog=None, tracker='default', log: Callable[[str], None] = print):
        self._run_task = run_task
        self._on_current_task = on_current_task
        self._on_step = on_step
        self._catalog = catalog if catalog is not None else load_catalog()
        self._tracker = make_tracker() if tracker == 'default' else tracker
        self._log = log
        self._abort = threading.Event()
        self._lock = threading.Lock()
        self._running = False
        self.state = IDLE
        self.current_app_id = ''

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
                return MissionResult(False, reason='; '.join(errors))
            self._running = True
            self._abort.clear()
            self.current_app_id = app_id or str(uuid.uuid4())

        types = [self._catalog.by_class(type(t)).name for t in tasks]
        ctx = a.MissionContext(
            tasks=list(tasks),
            task_types=types,
            arg_names={n: list(spec.args_schema) for n, spec in self._catalog.tasks.items()},
            run_task=self._run_task,
            abort_requested=self._abort.is_set,
            on_current_task=self._on_current_task,
            log=self._log,
            node_names=a.make_node_names(
                tasks, types, {n: spec.name_arg for n, spec in self._catalog.tasks.items()}),
        )
        app = build_mission_app(ctx, mission_id,
                                app_id=self.current_app_id, tracker=self._tracker)
        self.state = a.RUNNING
        final = None
        steps = []
        try:
            async for act, _result, state in app.aiterate(
                    halt_after=['idle'], inputs={'mission_id': mission_id}):
                final = state
                steps.append(act.name)
                self._on_step(act.name, state.get_all())
        finally:
            with self._lock:
                self._running = False
                self.state = IDLE

        return MissionResult(
            True,
            outcome=final['outcome'],
            burr_app_id=self.current_app_id,
            executed=list(final['executed']),
            steps=steps,
            message=final['message'],
        )

    async def run_llm(self, goal: str, planner, app_id: Optional[str] = None,
                      approve=None, feedback=None, robot=None, places=None,
                      on_plan=None) -> MissionResult:
        """LLM mode: the planner chooses tasks and blocks step by step (plan P6)."""
        from georg_task_manager.burr_app.builder import build_llm_app
        from georg_task_manager.burr_app.llm_actions import LLMContext

        with self._lock:
            if self._running:
                return MissionResult(
                    False, reason=f"mission '{self.current_app_id}' is still running")
            self._running = True
            self._abort.clear()
            self.current_app_id = app_id or str(uuid.uuid4())

        ctx = LLMContext(
            planner=planner, catalog=self._catalog, run_task=self._run_task,
            abort_requested=self._abort.is_set, on_current_task=self._on_current_task,
            log=self._log, approve=approve, feedback=feedback or (lambda: ''),
            robot=robot or (lambda: {}), places=list(places or []),
            on_plan=on_plan or (lambda plan: None), tracker=self._tracker)
        app = build_llm_app(ctx, 'llm', app_id=self.current_app_id, tracker=self._tracker)
        self.state = a.RUNNING
        final, steps = None, []
        try:
            async for act, _result, state in app.aiterate(halt_after=['idle'],
                                                          inputs={'goal': goal}):
                final = state
                steps.append(act.name)
                self._on_step(act.name, state.get_all())
        finally:
            with self._lock:
                self._running = False
                self.state = IDLE
        return MissionResult(True, outcome=final['outcome'], burr_app_id=self.current_app_id,
                             executed=list(final['executed']), steps=steps,
                             message=final['message'])

    def run_mission_blocking(self, mission_id: str, tasks: List[object]) -> MissionResult:
        return asyncio.run(self.run_mission(mission_id, tasks))
