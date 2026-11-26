from georg_task_manager.missions.DigitalFestival import get_mission as DigitalFestival
from georg_task_manager.missions.Test_Mapping import get_mission as TestMapping
from georg_task_manager.missions.Greeting import get_mission as Greeting
from georg_task_manager.missions.StartObjectFaceDetection import get_mission as StartObjectFaceDetection
from georg_task_manager.missions.StopObjectFaceDetection import get_mission as StopObjectFaceDetection
from georg_task_manager.missions.GreetPerson import get_mission as GreetPerson

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
        print("4 - Vision on")
        print("5 - Vision off")
        print("6 - Greet person V2")
        print("7 - Party Reception")
        print("0 - Exit")

        mission_id = input("\nSelect Mission: ")

    if mission_id == "1":
        return DigitalFestival()

    elif mission_id == "2":
        return TestMapping()

    elif mission_id == "3":
        return Greeting() #say hello

    elif mission_id == "4":
        return StartObjectFaceDetection()

    elif mission_id == "5":
        return StopObjectFaceDetection()

    elif mission_id =="6":
        return GreetPerson() #wave

    elif mission_id == "0":
        return None

    else:
        print("\nInvalid selection.\n")
