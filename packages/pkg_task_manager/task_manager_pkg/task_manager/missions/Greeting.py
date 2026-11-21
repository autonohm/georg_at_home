"""Greeting: Georg introduces himself (from branch pib_backend_integration, leakmpf)."""

from task_manager.tasks.Speak import Speak


def get_mission():
    """Say hello and ask for the name."""
    return [
        Speak("Hallo, ich bin Geeeorg, meine Freunde nennen mich Schorsch."),
        Speak("Wie ist dein Name?"),
    ]
