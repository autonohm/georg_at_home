from georg_task_manager.tasks.Speak import Speak
from georg_task_manager.tasks.Listen import Listen
from georg_task_manager.tasks.Listen import extract_name



def get_mission():
    print("[MISSION] Greeting started")

    ask_name = Listen()

    return [
        Speak("Hallo, ich bin Geeeorg, meine Freunde nennen mich Schorsch."),
        Speak("Wie ist dein Name?"),
        ask_name,
        Speak(lambda state: f"Schön, dich kennenzulernen {extract_name(ask_name.text) or 'du'}!"),
    ]