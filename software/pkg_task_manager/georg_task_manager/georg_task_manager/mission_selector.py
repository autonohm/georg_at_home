from georg_task_manager.missions.DigitalFestival import get_mission as DigitalFestival
from georg_task_manager.missions.Test_Mapping import get_mission as TestMapping
from georg_task_manager.missions.Greeting import get_mission as Greeting
from georg_task_manager.missions.ObjectFaceDetection import get_mission as ObjectFaceDetection

import os


def select_mission():
    mission_id = os.environ.get("MISSION_ID")

    if mission_id is None:
        print("\n==================================")
        print("         TASK MANAGER")
        print("==================================")
        print("1 - Digital Festival")
        print("2 - Mapping Test")
        print("3 - Greeting")
        print("4 - Vision")
        print("0 - Exit")

        mission_id = input("\nSelect Mission: ")

    if mission_id == "1":
        return DigitalFestival()

    elif mission_id == "2":
        return TestMapping()

    elif mission_id == "3":
        return Greeting()

    elif mission_id == "4":
        return ObjectFaceDetection()

    elif mission_id == "0":
        return None

    else:
        print("\nInvalid selection.\n")
