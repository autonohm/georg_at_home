"""Short mission for the mock scenarios (P2): one task of every package, short timeouts.

Not for the robot. The map comes from GEORG_MAP_DIR (default /root/georg_maps).
"""

import os

from task_manager.tasks.Gesture import Gesture
from task_manager.tasks.Listening import Listening
from task_manager.tasks.NavigateObject import NavigateObject
from task_manager.tasks.priority import CRITICAL, LOW
from task_manager.tasks.ReturnToIdle import ReturnToIdle

MAP = os.path.join(os.environ.get('GEORG_MAP_DIR', '/root/georg_maps'), 'Nav_Test.yaml')


def get_mission():
    return [
        Listening('DOORBELL', timeout_sec=3.0, priority=LOW),
        Gesture('look_at', -1000.0, 0.0, 100.0, priority=CRITICAL),
        NavigateObject('Seat', MAP),
        ReturnToIdle(),
    ]
