# speak.py - Georg says a text (ported from branch pib_backend_integration, leakmpf)
#
# The branch called the pib-backend service /play_audio_from_speech directly. Here the task
# uses the action speech/say (georg_speech_msgs/Say) like every other task, so the catalog,
# the mocks, the start check and cancel work the same way. pkg_pib_bridge serves speech/say
# and calls /play_audio_from_speech of pib-backend behind it.
from georg_speech_msgs.action import Say

from .base import BaseTask
from .priority import TaskPriority
from .timeout_watcher import wait_for_action_result

# default voice of Georg (same as in the branch)
# TODO: make these configurable elsewhere
DEFAULT_GENDER = "M1"
DEFAULT_LANGUAGE = "de"
DEFAULT_TIMEOUT = 60.0


class Speak(BaseTask):

    def __init__(self, text: str, priority: TaskPriority = TaskPriority.LOW,
                 gender: str = DEFAULT_GENDER, language: str = DEFAULT_LANGUAGE,
                 timeout: float = DEFAULT_TIMEOUT):
        super().__init__("Speak", priority)
        self.text = text
        self.gender = gender
        self.language = language
        self.timeout = float(timeout)

    def _resolve_text(self, state) -> str:
        # text can be a function of the state, e.g. a name heard by an earlier Listening task
        # (branch pib_backend_integration, leakmpf)
        value = self.text(state) if callable(self.text) else self.text
        return "" if value is None else str(value).strip()

    async def run(self, robot, state):
        try:
            text = self._resolve_text(state)
        except Exception as exc:  # noqa: BLE001 - a broken text function fails the task
            print(f"[TASK] Speak: could not build text: {exc!r}")
            return False
        if not text:
            print("[TASK] Speak: nothing to say")
            return False
        print(f"[TASK] Speak: '{text}'")
        goal = Say.Goal()
        goal.text = text
        goal.gender = self.gender
        goal.language = self.language
        result = await wait_for_action_result(
            robot.say_action_client,
            goal,
            timeout=self.timeout,
            abort_check=lambda: getattr(state, "abort_requested", False),
        )
        if result is None:
            print("[TASK] Speak: REJECTED/TIMEOUT/ABORTED")
            return False
        if not result.success:
            print(f"[TASK] Speak: FAILED ({result.message})")
            return False
        print("[TASK] Speak: Finished successfully")
        return True
