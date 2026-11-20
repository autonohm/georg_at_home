import os

from georg_task_manager.missions.DigitalFestival import get_mission as DigitalFestival
from georg_task_manager.missions.Mock_Test import get_mission as MockTest
from georg_task_manager.missions.Sim_Test import get_mission as SimSeat
from georg_task_manager.missions.Sim_Test import get_mission_door as SimDoor
from georg_task_manager.missions.Test_Mapping import get_mission as TestMapping


# Missions that can be started via the /task_manager/start service (P2).
# id -> (name shown in Lichtblick, function that returns the task list)
# To add a mission: write missions/<Name>.py with get_mission() and add one line here.
MISSIONS = {
    'digital_festival': ('Digital Festival', DigitalFestival),
    'test_mapping': ('Mapping Test', TestMapping),
    'mock_test': ('Mock Test (nur mit Mock-Paketen)', MockTest),
    'sim_seat': ('Simulation: zum Sitzplatz fahren', SimSeat),
    'sim_door': ('Simulation: zur Tür fahren', SimDoor),
}

# old menu numbers, still accepted as mission id
ALIASES = {'1': 'digital_festival', '2': 'test_mapping'}


def get_mission(mission_id: str):
    """Task list of a mission, or None if the id is unknown."""
    entry = MISSIONS.get(ALIASES.get(mission_id, mission_id))
    return entry[1]() if entry else None


def select_mission():
    """Interactive menu of the command line variant (task_manager_cli)."""
    mission_id = os.environ.get('MISSION_ID')

    if mission_id is None:
        print('\n==================================')
        print('         TASK MANAGER')
        print('==================================')
        print('1 - Digital Festival')
        print('2 - Mapping Test')
        print('0 - Exit')

        mission_id = input('\nSelect Mission: ')

    if mission_id == '1':
        return DigitalFestival()

    elif mission_id == '2':
        return TestMapping()

    elif mission_id == '0':
        return None

    else:
        print('\nInvalid selection.\n')
