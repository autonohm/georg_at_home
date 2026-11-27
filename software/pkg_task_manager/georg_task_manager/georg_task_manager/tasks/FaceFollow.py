# FaceFollow.py
from .base import BaseTask
from .timeout_watcher import wait_for_action_result
from .priority import TaskPriority
from geometry_msgs.msg import Vector3
from pib_gestures_action.action import PibGesturesInterface


class GestureFaceFollow(BaseTask):

    def __init__(
        self,
        priority: TaskPriority = TaskPriority.MID
    ):
        super().__init__("face_follow", priority)
        self.mode = "face_follow"

    async def run(self, robot, state):

        print(f"[TASK] Gesture {self.mode}: Started")

        goal_msg = PibGesturesInterface.Goal()
        goal_msg.pib_gesture = self.mode
        goal_msg.pib_side = "none"
        goal_msg.pib_mode = "none"
        goal_msg.pib_hand = "none"

        state.is_following_face = True

        result = await wait_for_action_result(
            robot.greet_action_client,
            goal_msg,
            timeout = 15.0,
            abort_check = lambda: getattr(state, "abort_requested", False),
        )

        state.is_following_face = False

        # Debug: hier steht die Fehlerursache vom Server
        if result is not None:
            print(f"[TASK] Gesture {self.mode}: success={result.success} message={getattr(result, 'message', '')}")

        if result is None:
            print(f"[TASK] Gesture {self.mode}: REJECTED/TIMEOUT/ABORTED")
            return False

        if result.success != 0:
            print(f"[TASK] Gesture {self.mode}: FAILED")
            return False

        print(f"[TASK] Gesture {self.mode}: Finished successfully")
        return True