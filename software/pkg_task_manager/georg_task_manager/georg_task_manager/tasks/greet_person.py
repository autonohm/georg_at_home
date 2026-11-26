# greet_guest.py
from .base import BaseTask
from .timeout_watcher import wait_for_action_result
from .priority import TaskPriority
from geometry_msgs.msg import Vector3
from pib_gestures_action.action import PibGesturesInterface


class GestureGreetPerson(BaseTask):

    def __init__(
        self,
        vx: float = None,
        vy: float = None,
        vz: float = None,
        pib_side: str = "None",
        pib_mode: str = "None",
        priority: TaskPriority = TaskPriority.LOW
    ):
        
        super().__init__("greet_person", priority)
        self.mode = "greet_person"
        self.vx = vx
        self.vy = vy
        self.vz = vz
        self.pib_side = pib_side
        self.pib_mode = pib_mode

    async def run(self, robot, state):

        print(f"[TASK] Gesture {self.mode}: Started")

        goal_msg = PibGesturesInterface.Goal()
        goal_msg.pib_gesture = self.mode
        goal_msg.input_vector = Vector3(x = self.vx, y = self.vy, z = self.vz)
        goal_msg.pib_side = self.pib_side
        goal_msg.pib_mode = self.pib_mode

        state.is_greeting_person = True

        result = await wait_for_action_result(
            robot.greet_action_client,
            goal_msg,
            timeout = 15.0,
            abort_check = lambda: getattr(state, "abort_requested", False),
        )

        state.is_greeting_person = False

        if result is None:
            print(f"[TASK] Gesture {self.mode}: REJECTED/TIMEOUT/ABORTED")
            return False

        if result.success != 0:
            print(f"[TASK] Gesture {self.mode}: FAILED")
            return False

        print(f"[TASK] Gesture {self.mode}: Finished successfully")
        return True