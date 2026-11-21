from georg_task_manager.tasks.Speak import Speak
from georg_task_manager.tasks.Listen import Listen


def get_mission():
    print("[MISSION] Greeting started")
    return [
        Speak("Hallo, ich bin Geeeorg, meine Freunde nennen mich Schorsch."),
        Speak("Wie ist dein Name?"),
        Listen(),
    ]