"""Missions that can be started via the task_manager/start service.

One mission per file with get_mission() returning the task list; register it in MISSIONS.
id -> (name shown in Lichtblick, function that returns the task list)
"""

from task_manager.missions import (DigitalFestival, Greeting, Mock_Test, Sim_Test,
                                   Test_Mapping)

MISSIONS = {
    'digital_festival': ('Digital Festival', DigitalFestival.get_mission),
    'test_mapping': ('Mapping Test', Test_Mapping.get_mission),
    'mock_test': ('Mock Test (nur mit Mock-Paketen)', Mock_Test.get_mission),
    'sim_seat': ('Simulation: zum Sitzplatz fahren', Sim_Test.get_mission),
    'sim_door': ('Simulation: zur Tür fahren', Sim_Test.get_mission_door),
    'sim_reset': ('Simulation: zurücksetzen (Start, Karte leer)', Sim_Test.get_mission_reset),
    'greeting': ('Begrüßung (spricht über pib-backend)', Greeting.get_mission),
}
# old numeric ids (MISSION_ID=1/2)
ALIASES = {'1': 'digital_festival', '2': 'test_mapping'}


def get_mission(mission_id: str):
    """Task list of a mission, or None if the id is unknown."""
    entry = MISSIONS.get(mission_id)
    return entry[1]() if entry else None
