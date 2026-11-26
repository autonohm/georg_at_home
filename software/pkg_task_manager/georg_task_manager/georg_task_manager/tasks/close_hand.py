# greet_guest.py
from .base import BaseTask
from .timeout_watcher import wait_for_action_result
from .priority import TaskPriority
from geometry_msgs.msg import Vector3
from pib_gestures_action.action import PibGesturesInterface


class GestureCloseHand(BaseTask):

    def __init__(
        self,
        pib_side: str = "None",
        priority: TaskPriority = TaskPriority.LOW
    ):
        
        super().__init__("close_hand", priority)
        self.mode = "close_hand"
        self.pib_side = pib_side

    async def run(self, robot, state):

        print(f"[TASK] Gesture {self.mode}: Started")

        goal_msg = PibGesturesInterface.Goal()
        goal_msg.pib_gesture = self.mode
        goal_msg.pib_side = self.pib_side

        state.is_offering_hand = True

        result = await wait_for_action_result(
            robot.greet_action_client,
            goal_msg,
            timeout = 15.0,
            abort_check = lambda: getattr(state, "abort_requested", False),
        )

        state.is_offering_hand = False

        if result is None:
            print(f"[TASK] Gesture {self.mode}: REJECTED/TIMEOUT/ABORTED")
            return False

        if result.success != 0:
            print(f"[TASK] Gesture {self.mode}: FAILED")
            return False

        print(f"[TASK] Gesture {self.mode}: Finished successfully")
        return True