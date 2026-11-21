# pib_pose.py - move pib to a named pose or sequence (e.g. winken, zeigen, ruhe)
#
# Served by fake_pib_motors in the simulation (pkg_pib_model, config/pib_poses.yaml).
# Not the gesture package: it computes gestures but sends no joint commands yet (Q34).
from georg_gesture_msgs.action import PibPose as PibPoseAction

from .base import BaseTask
from .priority import TaskPriority
from .timeout_watcher import wait_for_action_result


class PibPose(BaseTask):

    def __init__(self, pose: str, priority: TaskPriority = TaskPriority.LOW):
        super().__init__(f"PibPose({pose})", priority)
        self.pose = pose

    async def run(self, robot, state):
        print(f"[TASK] PibPose {self.pose}: started")
        goal = PibPoseAction.Goal()
        goal.pose = self.pose
        result = await wait_for_action_result(
            robot.pib_pose_action_client,
            goal,
            timeout=30.0,
            abort_check=lambda: getattr(state, "abort_requested", False),
        )
        if result is None:
            print(f"[TASK] PibPose {self.pose}: REJECTED/TIMEOUT/ABORTED")
            return False
        print(f"[TASK] PibPose {self.pose}: {result.message}")
        return bool(result.success)
