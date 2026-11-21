from georg_task_manager.tasks.Speak import Speak


def get_mission():
    print("[MISSION] Greeting started")
    return [
        Speak("Hallo, ich bin Geeeorg, meine Freunde nennen mich Schorsch."),
        Speak("Wie ist dein Name?"),
    ]