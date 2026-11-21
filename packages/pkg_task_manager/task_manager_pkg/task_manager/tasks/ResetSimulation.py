# reset_simulation.py - simulator back to the start (profile sim only)
from georg_sim_msgs.action import ResetSim

from .base import BaseTask
from .priority import TaskPriority
from .timeout_watcher import wait_for_action_result


class ResetSimulation(BaseTask):

    def __init__(self, clear_map: bool = True, priority: TaskPriority = TaskPriority.CRITICAL):
        super().__init__("ResetSimulation", priority)
        self.clear_map = bool(clear_map)

    async def run(self, robot, state):
        print("[TASK] ResetSimulation: started")
        goal = ResetSim.Goal()
        goal.clear_map = self.clear_map
        result = await wait_for_action_result(
            robot.reset_sim_action_client,
            goal,
            timeout=15.0,
            abort_check=lambda: getattr(state, "abort_requested", False),
        )
        if result is None:
            print("[TASK] ResetSimulation: REJECTED/TIMEOUT/ABORTED")
            return False
        print(f"[TASK] ResetSimulation: {result.message}")
        return bool(result.success)
