"""Missions for the simulator (P3): real navigation, mocked speech and gestures.

The map comes from GEORG_MAP_DIR (default /root/georg_maps).
"""

import os

from task_manager.tasks.NavigateObject import NavigateObject
from task_manager.tasks.PibPose import PibPose
from task_manager.tasks.ResetSimulation import ResetSimulation
from task_manager.tasks.ReturnToIdle import ReturnToIdle

MAP = os.path.join(os.environ.get('GEORG_MAP_DIR', '/root/georg_maps'),
                   os.environ.get('GEORG_DEFAULT_MAP', 'Nav_Test.yaml'))


def get_mission():
    """Drive to the seat."""
    return [NavigateObject('Seat', MAP), ReturnToIdle()]


def get_mission_door():
    """Drive to the door."""
    return [NavigateObject('Door', MAP), ReturnToIdle()]


def get_mission_reset():
    """Put the simulated robot back to the start and clear the map."""
    return [ResetSimulation(clear_map=True)]


def get_mission_gestures():
    """Wave at the start, drive to the seat, point at it, arms down."""
    return [PibPose('ruhe'), PibPose('winken'), PibPose('ruhe'),
            NavigateObject('Seat', MAP), PibPose('zeigen'), PibPose('begruessen'),
            PibPose('ruhe'), ReturnToIdle()]


def get_mission_arena_tour():
    """Apartment (GEORG_MAP=Wohnung.yaml): through all four rooms, greet the people.

    The places of Wohnung.yaml are free standing spots already -> no standoff.
    """
    def go(place):
        return NavigateObject(place, MAP, standoff_m=0.0)

    return [PibPose('winken'), PibPose('ruhe'),
            go('Person_Wohnzimmer'), PibPose('begruessen'), PibPose('ruhe'),
            go('Sofa'), PibPose('zeigen'), PibPose('ruhe'),
            go('Schreibtisch'), go('Person_Buero'),
            PibPose('winken'), PibPose('ruhe'),
            go('Bett'), go('Kuehlschrank'),
            go('Mitte'), ReturnToIdle()]
