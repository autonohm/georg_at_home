"""Missions for the simulator (P3): real navigation, mocked speech and gestures.

The map comes from GEORG_MAP_DIR (default /root/georg_maps).
"""

import os

from georg_task_manager.tasks.NavigateObject import NavigateObject
from georg_task_manager.tasks.ReturnToIdle import ReturnToIdle

MAP = os.path.join(os.environ.get('GEORG_MAP_DIR', '/root/georg_maps'), 'Nav_Test.yaml')


def get_mission():
    """Drive to the seat."""
    return [NavigateObject('Seat', MAP), ReturnToIdle()]


def get_mission_door():
    """Drive to the door."""
    return [NavigateObject('Door', MAP), ReturnToIdle()]
