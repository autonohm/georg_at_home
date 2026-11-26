from .base import BaseTask
from .timeout_watcher import wait_for_action_result
from .priority import TaskPriority
from datatypes.action import RecordAudio
import re

# Vorerst feste Einstellungen
DEFAULT_MAX_SILENT_BEFORE = 8.0   # s: so lange auf Sprechbeginn warten
DEFAULT_MAX_SILENT_AFTER = 1.0    # s: Pause, nach der die Äußerung als beendet gilt
DEFAULT_STT_ENGINE = "local_whisper"           # leer: Backend-Default (STT_ENGINE, sonst local_whisper)
DEFAULT_INCLUDE_PREROLL = False   # nur für Barge-in sinnvoll
MAX_UTTERANCE_SECONDS = 20.0      # Puffer für die Dauer der Äußerung + Transkription


class Listen(BaseTask):

    def __init__(
        self,
        priority: TaskPriority = TaskPriority.LOW,
        max_silent_before: float = DEFAULT_MAX_SILENT_BEFORE,
        max_silent_after: float = DEFAULT_MAX_SILENT_AFTER,
        stt_engine: str = DEFAULT_STT_ENGINE,
        include_preroll: bool = DEFAULT_INCLUDE_PREROLL,
        timeout: float | None = None,
    ):
        super().__init__("Listen", priority)
        self.max_silent_before = max_silent_before
        self.max_silent_after = max_silent_after
        self.stt_engine = stt_engine
        self.include_preroll = include_preroll
        self.timeout = timeout or (max_silent_before + MAX_UTTERANCE_SECONDS + 10.0)
        self.text = None

    async def run(self, robot, state):

        print("[TASK] Listen: Started")

        goal_msg = RecordAudio.Goal()
        goal_msg.max_silent_seconds_before = float(self.max_silent_before)
        goal_msg.max_silent_seconds_after = float(self.max_silent_after)

        # Optionale Felder: nur setzen, wenn die .action sie enthält
        fields = goal_msg.get_fields_and_field_types()
        if "stt_engine" in fields and self.stt_engine:
            goal_msg.stt_engine = self.stt_engine
        if "include_preroll" in fields:
            goal_msg.include_preroll = self.include_preroll

        state.is_listening = True

        result = await wait_for_action_result(
            robot.listen_action_client,
            goal_msg,
            timeout=self.timeout,
            abort_check=lambda: getattr(state, "abort_requested", False),
        )

        state.is_listening = False

        if result is None:
            print("[TASK] Listen: REJECTED/TIMEOUT/ABORTED")
            return False

        # falls der Helper einen Result-Wrapper statt der Nachricht liefert
        result = getattr(result, "result", result)
        self.text = (result.transcribed_text or "").strip()
        state.last_heard_text = self.text

        if not self.text:
            print("[TASK] Listen: nothing recognized")
            return False

        print(f"[TASK] Listen: heard '{self.text}'")
        return True
    

def extract_name(text):
    if not text:
        return None
    t = text.strip().strip(".!?, ")
    m = re.search(
        r"(?:I am|I'm|my name is|call me)\s+(?:der |die )?(\w[\w\-]*)",
        t, flags=re.IGNORECASE)
    if m:
        return m.group(1).capitalize()
    words = t.split()
    return words[0].capitalize() if len(words) == 1 else None