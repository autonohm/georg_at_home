"""Greeting: Georg introduces himself, asks for the name and answers with it.

Ported from branch pib_backend_integration (leakmpf). Listening(SPEECH) goes to
pib-backend /record_audio through pkg_pib_bridge (speech-to-text), Speak to
/play_audio_from_speech. The last Speak builds its text from what was heard.
"""

import re

from task_manager.tasks.Listening import Listening
from task_manager.tasks.Speak import Speak

NAME_PATTERN = re.compile(
    r'(?:ich heiße|ich heisse|mein name ist|ich bin|man nennt mich|nenn mich)\s+'
    r'(?:der |die )?(\w[\w\-]*)',
    flags=re.IGNORECASE)


def extract_name(text):
    """Name from an answer like 'Ich heiße Anna' or just 'Anna'; None if not found."""
    if not text:
        return None
    t = text.strip().strip('.!?, ')
    m = NAME_PATTERN.search(t)
    if m:
        return m.group(1).capitalize()
    words = t.split()
    return words[0].capitalize() if len(words) == 1 else None


def get_mission():
    """Say hello, ask for the name, listen, greet by name."""
    ask_name = Listening('SPEECH', timeout_sec=8.0)
    return [
        Speak('Hallo, ich bin Geeeorg, meine Freunde nennen mich Schorsch.'),
        Speak('Wie ist dein Name?'),
        ask_name,
        Speak(lambda state: "Schön, dich kennenzulernen "
                            f"{extract_name(ask_name.text) or 'du'}!"),
    ]
