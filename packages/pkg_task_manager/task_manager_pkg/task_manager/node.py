r"""ROS bridge of the task manager (P2): the long-running task manager node.

Services (relative to EDU_ROBOT_NAMESPACE, default none, e.g. /task_manager/start):

    task_manager/start           StartMission    start a mission by id
    task_manager/cancel          CancelMission   abort the running mission
    task_manager/list_missions   ListMissions    missions for the Lichtblick dropdown

Topic:

    task_manager/status          MissionStatus   transient_local, updated on every Burr step

The node starts in Idle and never starts a mission by itself (plan: hard rules).
Missions run in Burr (engine/service.py) on an asyncio loop in a worker thread;
the node itself spins in a MultiThreadedExecutor so action results arrive while
a mission runs.

    ros2 service call /task_manager/start georg_task_manager_msgs/srv/StartMission \\
        "{mission_id: digital_festival}"
    ros2 service call /task_manager/cancel georg_task_manager_msgs/srv/CancelMission "{}"
"""

import asyncio
import json
import os
import threading
import traceback
import uuid

from georg_task_manager_msgs.msg import MissionStatus
from georg_task_manager_msgs.srv import ApprovePlan, CancelMission, Instruct, ListMissions
from georg_task_manager_msgs.srv import SetMode, StartMission
import rclpy
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String
from task_manager.catalog import load_catalog
from task_manager.catalog.validator import check_mission
from task_manager.engine.service import TaskManagerService
from task_manager.missions import ALIASES, get_mission, MISSIONS
from task_manager.planner.llm_client import LLMClient
from task_manager.planner.planner import Planner
from task_manager.robot import Georg
from task_manager.tasks.base import default_map_path

MODES = ('mission', 'llm', 'llm_approval')
APPROVAL_TIMEOUT_S = 300.0

OUTCOME_TO_STATE = {
    'succeeded': MissionStatus.SUCCEEDED,
    'failed': MissionStatus.FAILED,
    'aborted': MissionStatus.ABORTED,
}


class TaskManagerBridge(Node):

    def __init__(self):
        super().__init__('task_manager')
        self.declare_parameter('server_timeout_s', 1.0)
        self._cb = ReentrantCallbackGroup()
        self._profile = os.environ.get('GEORG_PROFILE', '')

        self.robot = Georg(self)
        self.state = self.robot.state
        self.catalog = load_catalog()
        self._action_clients = {c._action_name: c for c in vars(self.robot).values()
                                if isinstance(c, ActionClient)}

        # depth 10: fast Burr steps must not be dropped on the way to Lichtblick (foxglove_bridge)
        status_qos = QoSProfile(depth=10, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                                reliability=ReliabilityPolicy.RELIABLE)
        self._status_pub = self.create_publisher(MissionStatus, 'task_manager/status', status_qos)
        self.create_service(StartMission, 'task_manager/start', self._on_start,
                            callback_group=self._cb)
        self.create_service(CancelMission, 'task_manager/cancel', self._on_cancel,
                            callback_group=self._cb)
        self.create_service(ListMissions, 'task_manager/list_missions', self._on_list,
                            callback_group=self._cb)
        # P6: operating modes and the LLM planner
        self.create_service(SetMode, 'task_manager/set_mode', self._on_set_mode,
                            callback_group=self._cb)
        self.create_service(Instruct, 'task_manager/instruct', self._on_instruct,
                            callback_group=self._cb)
        self.create_service(ApprovePlan, 'task_manager/approve_plan', self._on_approve,
                            callback_group=self._cb)
        plan_qos = QoSProfile(depth=10, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                              reliability=ReliabilityPolicy.RELIABLE)
        self._plan_pub = self.create_publisher(String, 'task_manager/plan', plan_qos)
        # after the start always mission mode; the LLM only acts after the operator
        # switched to an LLM mode (plan: hard rules)
        self._mode = 'mission'
        self._feedback = ''
        self._approval = None
        self.llm = LLMClient()

        self.service = TaskManagerService(
            run_task=self._run_task,
            on_current_task=self._on_current_task,
            on_step=self._on_step,
            catalog=self.catalog,
            log=lambda line: self.get_logger().info(line.strip()) if line.strip() else None,
        )

        self._lock = threading.Lock()
        self._busy = False
        self._mission_id = ''
        self._app_id = ''
        self._loop = asyncio.new_event_loop()
        threading.Thread(target=self._loop.run_forever, name='burr-loop', daemon=True).start()

        self._publish(MissionStatus.IDLE, message='ready')
        self._publish_plan({'mode': self._mode})
        self.get_logger().info(
            f"task manager ready (Idle), profile='{self._profile or '-'}', "
            f"missions: {', '.join(MISSIONS)}")

    # --- services -------------------------------------------------------------

    def _on_start(self, request, response):
        response.accepted, response.reason, response.burr_app_id = False, '', ''
        mission_id = ALIASES.get(request.mission_id, request.mission_id)

        with self._lock:
            if self._busy:
                response.reason = f"mission '{self._mission_id}' is still running"
                return response
            self._busy = True
        try:
            reason = self._check_start(mission_id, request.params_json)
            if isinstance(reason, str):
                response.reason = reason
                with self._lock:
                    self._busy = False
                return response
            tasks = reason
        except Exception as exc:  # never leave the node busy because of a bug in a check
            with self._lock:
                self._busy = False
            response.reason = f'internal error: {exc}'
            return response

        app_id = str(uuid.uuid4())
        self._mission_id, self._app_id = mission_id, app_id
        self.state.abort_requested = False
        self.state.mission_running = True
        self.state.mission_finished = False
        future = asyncio.run_coroutine_threadsafe(
            self.service.run_mission(mission_id, tasks, app_id=app_id), self._loop)
        future.add_done_callback(self._on_mission_done)

        self._publish(MissionStatus.RUNNING, total_steps=len(tasks), message='started')
        self.get_logger().info(f"mission '{mission_id}' started, burr_app_id={app_id}")
        response.accepted, response.burr_app_id = True, app_id
        return response

    def _check_start(self, mission_id: str, params_json: str):
        """Return the task list, or a reason (str) why the mission cannot start."""
        if params_json.strip():
            try:
                json.loads(params_json)
            except ValueError as exc:
                return f'params_json is not valid JSON: {exc}'
        tasks = get_mission(mission_id)
        if tasks is None:
            return f"unknown mission '{mission_id}' (available: {', '.join(MISSIONS)})"
        errors = check_mission(tasks, self.catalog)
        if errors:
            return '; '.join(errors)

        specs = {self.catalog.by_class(type(t)).name: self.catalog.by_class(type(t))
                 for t in tasks}
        if self._profile:
            wrong = [n for n, s in specs.items() if self._profile not in s.modes]
            if wrong:
                return f"tasks {wrong} not allowed in mode '{self._profile}'"

        timeout = self.get_parameter('server_timeout_s').value
        missing = []
        for action in sorted({a for s in specs.values() for a in s.actions}):
            client = self._action_clients.get(action)
            if client is None:
                missing.append(f'{action} (no client in robot.py)')
            elif not client.wait_for_server(timeout_sec=timeout):
                missing.append(action)
        if missing:
            return 'action server not reachable: ' + ', '.join(missing)
        return tasks

    def _on_cancel(self, request, response):
        response.accepted, response.reason = False, ''
        if not self.service.running:
            response.reason = 'no mission running'
            return response
        wanted = ALIASES.get(request.mission_id, request.mission_id)
        if wanted and wanted != self._mission_id:
            response.reason = f"running mission is '{self._mission_id}', not '{wanted}'"
            return response
        # tasks poll state.abort_requested and cancel their action goal
        self.state.abort_requested = True
        self.service.request_abort()
        self.get_logger().info(f"abort requested for '{self._mission_id}'")
        response.accepted = True
        return response

    def _on_list(self, request, response):
        response.mission_ids = list(MISSIONS)
        response.display_names = [name for name, _ in MISSIONS.values()]
        return response

    def _on_set_mode(self, request, response):
        response.accepted, response.reason, response.mode = False, '', self._mode
        mode = request.mode.strip()
        if mode not in MODES:
            response.reason = f"unknown mode '{mode}' (available: {', '.join(MODES)})"
            return response
        if self.service.running:
            response.reason = 'not while a mission is running'
            return response
        if mode != 'mission' and self._profile == 'real' \
                and os.environ.get('GEORG_LLM_REAL_APPROVED') != '1':
            response.reason = ('LLM modes on the real robot only after passing the replay and '
                               'simulation tests (GEORG_LLM_REAL_APPROVED=1)')
            return response
        self._mode = mode
        self.get_logger().info(f'operating mode: {mode}')
        self._publish_plan({'mode': mode})
        response.accepted, response.mode = True, mode
        return response

    def _on_instruct(self, request, response):
        response.accepted, response.reason, response.burr_app_id = False, '', ''
        text = request.text.strip()
        if self._mode == 'mission':
            response.reason = 'switch to an LLM mode first (task_manager/set_mode)'
            return response
        if not text:
            response.reason = 'empty instruction'
            return response
        with self._lock:
            busy = self._busy
            if not busy:
                self._busy = True
        if busy:
            if self._mission_id != 'llm':
                response.reason = f"mission '{self._mission_id}' is running"
                return response
            self._feedback = text            # goes into the next decision of the planner
            response.accepted, response.burr_app_id = True, self._app_id
            return response
        if not self.llm.available():
            with self._lock:
                self._busy = False
            response.reason = f'LLM endpoint {self.llm.config.url} not reachable'
            return response

        planner = Planner(self.llm.chat, self.catalog, mode=self._profile or 'mock',
                          model=self.llm.model)
        app_id = str(uuid.uuid4())
        self._mission_id, self._app_id, self._feedback = 'llm', app_id, ''
        self.state.abort_requested = False
        self.state.mission_running = True
        approve = self._wait_for_approval if self._mode == 'llm_approval' else None
        future = asyncio.run_coroutine_threadsafe(
            self.service.run_llm(text, planner, app_id=app_id, approve=approve,
                                 feedback=self._take_feedback, robot=self._robot_summary,
                                 places=self._places(), on_plan=self._publish_plan),
            self._loop)
        future.add_done_callback(self._on_mission_done)
        self._publish(MissionStatus.RUNNING, message=f'LLM: {text}')
        self.get_logger().info(f"LLM run started: '{text}', burr_app_id={app_id}")
        response.accepted, response.burr_app_id = True, app_id
        return response

    def _on_approve(self, request, response):
        response.accepted, response.reason = False, ''
        pending = self._approval
        if pending is None or pending.done():
            response.reason = 'no plan waiting for approval'
            return response
        self._loop.call_soon_threadsafe(
            lambda: None if pending.done() else pending.set_result(bool(request.approve)))
        response.accepted = True
        return response

    async def _wait_for_approval(self, items, reason) -> bool:
        self._approval = self._loop.create_future()
        self._publish(MissionStatus.RUNNING, message='waiting for approval: ' + reason)
        try:
            end = self._loop.time() + APPROVAL_TIMEOUT_S
            while not self._approval.done():
                if self.service.abort_requested or self._loop.time() > end:
                    return False
                await asyncio.sleep(0.05)
            return self._approval.result()
        finally:
            self._approval = None

    def _take_feedback(self) -> str:
        text, self._feedback = self._feedback, ''
        return text

    def _robot_summary(self) -> dict:
        pos = self.state.current_position
        return {'position': [round(pos[0], 2), round(pos[1], 2)] if pos else None,
                'mode': self._profile}

    def _places(self):
        try:
            import yaml
            with open(default_map_path(), encoding='utf-8') as f:
                return sorted((yaml.safe_load(f) or {}).get('objects', {}) or {})
        except OSError:
            return []

    def _publish_plan(self, plan: dict) -> None:
        msg = String()
        msg.data = json.dumps(dict(plan, mode=self._mode), ensure_ascii=False)
        self._plan_pub.publish(msg)

    # --- mission execution ----------------------------------------------------

    async def _run_task(self, task) -> bool:
        return await task.run(self.robot, self.state)

    def _on_current_task(self, name: str) -> None:
        self.state.current_task = name
        msg = String()
        msg.data = name
        self.robot.taskmanager_current_task_pub.publish(msg)

    def _on_step(self, action: str, state: dict) -> None:
        if action in ('finish', 'idle'):
            return
        if 'goal' in state:                 # LLM run
            current = state.get('current') or {}
            name = current.get('block') or current.get('task') or ''
            history = state.get('history', [])
            self._publish(MissionStatus.RUNNING, current_task=name, step=len(history),
                          total_steps=len(history) + len(state.get('remaining', [])) + 1,
                          message=state.get('message', ''))
            return
        self._publish(
            MissionStatus.RUNNING,
            current_task=state.get('next_task') or state.get('task') or '',
            step=int(state.get('step', 0)),
            total_steps=len(state.get('planned', [])),
            message=state.get('decision', ''),
        )

    def _on_mission_done(self, future) -> None:
        self.state.mission_running = False
        try:
            result = future.result()
        except Exception as exc:
            self.get_logger().error(
                f"mission '{self._mission_id}' crashed: {exc}\n{traceback.format_exc()}")
            self._publish(MissionStatus.FAILED, message=f'crashed: {exc}')
        else:
            if not result.accepted:
                self._publish(MissionStatus.FAILED, message=result.reason)
            else:
                self.state.mission_finished = result.outcome == 'succeeded'
                self._publish(OUTCOME_TO_STATE.get(result.outcome, MissionStatus.FAILED),
                              step=len(result.executed), message=result.message)
                self.get_logger().info(
                    f"mission '{self._mission_id}' {result.outcome}: {result.message}")
        with self._lock:
            self._busy = False

    def _publish(self, state: int, current_task: str = '', step: int = 0,
                 total_steps: int = 0, message: str = '') -> None:
        msg = MissionStatus()
        msg.state = state
        msg.mission_id = self._mission_id
        msg.current_task = current_task
        msg.step = max(0, min(step, 65535))
        msg.total_steps = max(0, min(total_steps, 65535))
        msg.message = message
        msg.burr_app_id = self._app_id
        msg.stamp = self.get_clock().now().to_msg()
        self._status_pub.publish(msg)

    def shutdown(self) -> None:
        if self.service.running:
            self.state.abort_requested = True
            self.service.request_abort()
        self._loop.call_soon_threadsafe(self._loop.stop)


def main(args=None):
    rclpy.init(args=args)
    node = TaskManagerBridge()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.shutdown()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
