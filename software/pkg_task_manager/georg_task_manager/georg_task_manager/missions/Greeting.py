from georg_task_manager.tasks.Speak import Speak
from georg_task_manager.tasks.Listen import Listen
from georg_task_manager.tasks.Listen import extract_name
from georg_task_manager.tasks.Remember import Remember



def get_mission():
    print("[MISSION] Greeting started")

    ask_name = Listen()
    name = None

    def store_name(state):
        nonlocal name
        name = extract_name(ask_name.text)
        print(f"[MISSION] Name stored: {name}")

    return [
        Speak("Hi, my name is Georg."),
        Speak("What's your name?"),
        ask_name,
        Remember(store_name),
        Speak(lambda state: f"Nice to meet you { name or ''}!"),
        Speak(lambda state: f"{ name or ''}, please follow me to the living room."),
    ]
