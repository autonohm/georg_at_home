from georg_task_manager.tasks.Speak import Speak
from georg_task_manager.tasks.Listen import Listen
import re

def extract_name(text):
    if not text:
        return None
    t = text.strip().strip(".!?, ")
    m = re.search(
        r"(?:ich heiße|ich heisse|mein name ist|ich bin|man nennt mich|nenn mich)\s+(?:der |die )?(\w[\w\-]*)",
        t, flags=re.IGNORECASE)
    if m:
        return m.group(1).capitalize()
    words = t.split()
    return words[0].capitalize() if len(words) == 1 else None


def get_mission():
    print("[MISSION] Greeting started")

    ask_name = Listen()

    return [
        Speak("Hallo, ich bin Geeeorg, meine Freunde nennen mich Schorsch."),
        Speak("Wie ist dein Name?"),
        ask_name,
        Speak(lambda state: f"Schön, dich kennenzulernen {extract_name(ask_name.text) or 'du'}!"),
    ]