"""Greeting mission: name extraction and the text built from what was heard (no ROS needed)."""

import asyncio
from types import SimpleNamespace

import pytest
from task_manager.missions.Greeting import extract_name, get_mission


@pytest.mark.parametrize('heard, name', [
    ('Ich heiße Anna.', 'Anna'),
    ('mein Name ist der Paul', 'Paul'),
    ('Hallo, ich bin lena-marie!', 'Lena-marie'),
    ('Tom', 'Tom'),
    ('', None),
    ('Das weiß ich nicht so genau', None),
])
def test_extract_name(heard, name):
    assert extract_name(heard) == name


def test_last_speak_uses_the_heard_name():
    tasks = get_mission()
    listening, answer = tasks[2], tasks[3]
    state = SimpleNamespace()
    listening.text = 'Ich heiße Anna'
    assert answer._resolve_text(state) == 'Schön, dich kennenzulernen Anna!'
    listening.text = None
    assert answer._resolve_text(state) == 'Schön, dich kennenzulernen du!'


def test_speak_with_empty_text_fails_without_calling_anything():
    from task_manager.tasks.Speak import Speak
    assert asyncio.run(Speak(lambda s: '').run(robot=None, state=SimpleNamespace())) is False
