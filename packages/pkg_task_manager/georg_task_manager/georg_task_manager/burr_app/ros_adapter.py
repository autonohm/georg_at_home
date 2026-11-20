"""Drop-in replacement for ``task_manager.TaskManager``, backed by Burr.

Same constructor and the same ``run(tasks)`` / ``request_abort()`` as before,
so ``main.py`` only swaps the class. Services, status topic and mission list
follow in P2 (``ros_bridge.py``).
"""

import os

from georg_task_manager.burr_app.service import TaskManagerService


class BurrTaskManager:

    def __init__(self, robot, state, current_task_pub, mission_id: str = ""):
        self.robot = robot
        self.state = state
        self.current_task_pub = current_task_pub
        self.mission_id = mission_id or os.environ.get("MISSION_ID", "mission")
        self.service = TaskManagerService(
            run_task=self._run_task,
            on_current_task=self._on_current_task,
        )
        self.last_result = None

    def request_abort(self):
        # tasks poll state.abort_requested inside wait_for_action_result
        self.state.abort_requested = True
        self.service.request_abort()

    async def _run_task(self, task) -> bool:
        return await task.run(self.robot, self.state)

    def _on_current_task(self, name: str) -> None:
        self.state.current_task = name
        self._publish_task_state(name)

    async def run(self, tasks) -> bool:
        self.state.mission_running = True
        self.state.mission_finished = False
        self.state.abort_requested = False

        result = await self.service.run_mission(self.mission_id, tasks)
        self.last_result = result

        self.state.mission_running = False
        if not result.accepted:
            print(f"[MISSION REJECTED] {result.reason}")
            return False

        print(f"[BURR] run {result.burr_app_id}: {result.outcome}")
        if result.outcome == "succeeded":
            self.state.mission_finished = True
            return True
        return False

    def _publish_task_state(self, name: str) -> None:
        import rclpy
        from std_msgs.msg import String

        if not rclpy.ok():
            return
        msg = String()
        msg.data = name
        try:
            self.current_task_pub.publish(msg)
        except rclpy._rclpy_pybind11.RCLError:
            pass
