# greet_guest.py
from .base import BaseTask
from .timeout_watcher import wait_for_service_result
from .priority import TaskPriority
from datatypes.srv import PlayAudioFromSpeech

# default parameters for georg's voice
# todo: make these parameters configurable elsewhere
DEFAULT_GENDER = "M1"
DEFAULT_LANGUAGE = "de"
DEFAULT_JOIN = True
DEFAULT_TIMEOUT = 60.0


class Speak(BaseTask):

    def __init__(
        self,
        text: str,
        priority: TaskPriority = TaskPriority.LOW,
        gender: str = DEFAULT_GENDER,
        language: str = DEFAULT_LANGUAGE,
        join: bool = DEFAULT_JOIN,
        timeout: float = DEFAULT_TIMEOUT,
    ):

        super().__init__("Speak", priority)
        self.text = text
        self.gender = gender
        self.language = language
        self.join = join
        self.timeout = timeout

    def _resolve_text(self, state) -> str:
        value = self.text(state) if callable(self.text) else self.text
        return "" if value is None else str(value).strip()

    async def run(self, robot, state):

        print("[TASK] Speak: Started")

        try:
            text = self._resolve_text(state)
        except Exception as exc:
            print(f"[TASK] Speak: could not build text: {exc!r}")
            return False

        if not text:
            print("[TASK] Speak: nothing to say")
            return False

        print(f"[TASK] Speak: {text}")

        request = PlayAudioFromSpeech.Request()
        request.speech = text
        request.gender = self.gender
        request.language = self.language
        request.join = self.join

        result = await wait_for_service_result(
            robot.speak_service_client,
            request,
            timeout=self.timeout,
            abort_check=lambda: getattr(state, "abort_requested", False),
        )

        if result is None:
            print(f"[TASK] Speak: REJECTED/TIMEOUT/ABORTED")
            return False

        print(f"[TASK] Speak: Finished successfully")
        return True
    