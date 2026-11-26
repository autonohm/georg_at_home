# offer_and_close_hand.py
import asyncio

from .base import BaseTask
from .priority import TaskPriority
from .offer_hand import GestureOfferHand
from .close_hand import GestureCloseHand   # class in close_hand.py must be renamed (currently GestureOpenHand)


class GestureOfferCloseHand(BaseTask):
    """Offer the hand, wait `wait_time` seconds, then close the hand.

    On abort the hand stays in its current pose (no close_hand is sent).
    """

    def __init__(
        self,
        pib_side: str = "None",
        pib_mode: str = "None",
        wait_time: float = 5.0,
        priority: TaskPriority = TaskPriority.LOW
    ):

        super().__init__("offer_and_close_hand", priority)
        self.pib_side = pib_side
        self.pib_mode = pib_mode
        self.wait_time = wait_time

    async def run(self, robot, state):

        print("[TASK] offer_and_close_hand: Started")

        abort = lambda: getattr(state, "abort_requested", False)

        # 1. offer hand
        offer = GestureOfferHand(
            pib_side = self.pib_side,
            pib_mode = self.pib_mode,
            priority = self.priority,
        )
        if not await offer.run(robot, state):
            print("[TASK] offer_and_close_hand: offer_hand failed/aborted")
            return False

        # 2. wait (polling so an abort is noticed; hand stays as it is)
        elapsed = 0.0
        step = 0.1
        while elapsed < self.wait_time:
            if abort():
                print("[TASK] offer_and_close_hand: ABORTED, hand left in pose")
                return False
            await asyncio.sleep(step)
            elapsed += step

        if abort():
            print("[TASK] offer_and_close_hand: ABORTED, hand left in pose")
            return False

        # 3. close hand
        close = GestureCloseHand(
            pib_side = self.pib_side,
            priority = self.priority,
        )
        if not await close.run(robot, state):
            print("[TASK] offer_and_close_hand: close_hand failed/aborted")
            return False

        print("[TASK] offer_and_close_hand: Finished successfully")
        return True