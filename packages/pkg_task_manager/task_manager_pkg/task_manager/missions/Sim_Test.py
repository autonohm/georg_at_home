"""Missions for the simulator (P3): real navigation, mocked speech and gestures.

The map is the current world of the simulator (tasks/base.py default_map_path), read when
the mission starts, so a world switch in Lichtblick applies to the next mission.
"""

from task_manager.tasks.NavigateObject import NavigateObject
from task_manager.tasks.PibPose import PibPose
from task_manager.tasks.ResetSimulation import ResetSimulation
from task_manager.tasks.ReturnToIdle import ReturnToIdle
from task_manager.tasks.base import default_map_path


def get_mission():
    """Drive to the seat."""
    return [NavigateObject('Seat', default_map_path()), ReturnToIdle()]


def get_mission_door():
    """Drive to the door."""
    return [NavigateObject('Door', default_map_path()), ReturnToIdle()]


def get_mission_reset():
    """Put the simulated robot back to the start and clear the map."""
    return [ResetSimulation(clear_map=True)]


def get_mission_gestures():
    """Wave at the start, drive to the seat, point at it, arms down."""
    return [PibPose('ruhe'), PibPose('winken'), PibPose('ruhe'),
            NavigateObject('Seat', default_map_path()), PibPose('zeigen'), PibPose('begruessen'),
            PibPose('ruhe'), ReturnToIdle()]


def get_mission_arena_tour():
    """Apartment (GEORG_MAP=Wohnung.yaml): through all four rooms, greet the people.

    The places of Wohnung.yaml are free standing spots already -> no standoff.
    """
    def go(place):
        return NavigateObject(place, default_map_path(), standoff_m=0.0)

    return [PibPose('winken'), PibPose('ruhe'),
            go('Person_Wohnzimmer'), PibPose('begruessen'), PibPose('ruhe'),
            go('Sofa'), PibPose('zeigen'), PibPose('ruhe'),
            go('Schreibtisch'), go('Person_Buero'),
            PibPose('winken'), PibPose('ruhe'),
            go('Bett'), go('Kuehlschrank'),
            go('Mitte'), ReturnToIdle()]
