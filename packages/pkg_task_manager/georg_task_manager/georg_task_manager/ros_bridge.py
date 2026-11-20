r"""ROS bridge of the task manager (P2): the long-running task manager node.

Services (relative to the robot namespace, e.g. /georg/task_manager/start):

    task_manager/start           StartMission    start a mission by id
    task_manager/cancel          CancelMission   abort the running mission
    task_manager/list_missions   ListMissions    missions for the Lichtblick dropdown

Topic:

    task_manager/status          MissionStatus   transient_local, updated on every Burr step

The node starts in Idle and never starts a mission by itself (plan: hard rules).
Missions run in Burr (burr_app/service.py) on an asyncio loop in a worker thread;
the node itself spins in a MultiThreadedExecutor so action results arrive while
a mission runs.

    ros2 service call /georg/task_manager/start georg_task_manager_msgs/srv/StartMission \\
        "{mission_id: digital_festival}"
    ros2 service call /georg/task_manager/cancel georg_task_manager_msgs/srv/CancelMission "{}"
"""

import asyncio
import json
import os
import threading
import traceback
import uuid

from georg_task_manager.burr_app.service import TaskManagerService
from georg_task_manager.catalog import load_catalog
from georg_task_manager.Georg import Georg
from georg_task_manager.mission_selector import ALIASES, get_mission, MISSIONS
from georg_task_manager.validator import check_mission
from georg_task_manager_msgs.msg import MissionStatus
from georg_task_manager_msgs.srv import CancelMission, ListMissions, StartMission
import rclpy
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
from rclpy.node import Node
from rclpy.qos import DurabilityPolicy, QoSProfile, ReliabilityPolicy
from std_msgs.msg import String

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
                missing.append(f'{action} (no client in Georg.py)')
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
