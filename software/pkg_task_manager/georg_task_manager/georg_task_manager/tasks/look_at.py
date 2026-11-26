# greet_guest.py
from .base import BaseTask
from .timeout_watcher import wait_for_action_result
from .priority import TaskPriority
from geometry_msgs.msg import Vector3
from pib_gestures_action.action import PibGesturesInterface


class GestureLookAt(BaseTask):

    def __init__(
        self,
        vx: float = None,
        vy: float = None,
        vz: float = None,
        priority: TaskPriority = TaskPriority.LOW
    ):
        
        super().__init__("look_at", priority)
        self.mode = "look_at"
        self.vx = vx
        self.vy = vy
        self.vz = vz

    async def run(self, robot, state):

        print(f"[TASK] Gesture {self.mode}: Started")

        goal_msg = PibGesturesInterface.Goal()
        goal_msg.pib_gesture = self.mode
        goal_msg.input_vector = Vector3(x = self.vx, y = self.vy, z = self.vz)

        state.is_looking_at_object = True

        result = await wait_for_action_result(
            robot.greet_action_client,
            goal_msg,
            timeout = 15.0,
            abort_check = lambda: getattr(state, "abort_requested", False),
        )

        state.is_looking_at_object = False

        if result is None:
            print(f"[TASK] Gesture {self.mode}: REJECTED/TIMEOUT/ABORTED")
            return False

        if result.success != 0:
            print(f"[TASK] Gesture {self.mode}: FAILED")
            return False

        print(f"[TASK] Gesture {self.mode}: Finished successfully")
        return True