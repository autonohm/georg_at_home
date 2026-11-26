from georg_task_manager.tasks.Speak import Speak
from georg_task_manager.tasks.Listen import Listen
from georg_task_manager.tasks.Listen import extract_name
from georg_task_manager.tasks.StartFaceTracking import StartFaceTracking
from georg_task_manager.tasks.StopFaceTracking import StopFaceTracking
from georg_task_manager.tasks.StartObjectDetection import StartObjectDetection
from georg_task_manager.tasks.StopObjectDetection import StopObjectDetection
from georg_task_manager.tasks.priority import TaskPriority
from georg_task_manager.tasks.Remember import Remember
from georg_task_manager.tasks.DescribeScene import DescribeScene
from georg_task_manager.tasks.FaceFollow import GestureFaceFollow # GestureOfferCloseHand, GestureCloseHand, GestureOpenHand, GestureGreetPerson, GestureLookAt, GestureOfferHand, GesturePointTo



def get_mission():
    print("[MISSION] Qualification started")

    ask_name = Listen()
    name = None

    def store_name(state):
        nonlocal name
        name = extract_name(ask_name.text)
        print(f"[MISSION] Name stored: {name}")

    return [

        # start vision models
        StartObjectDetection(priority=TaskPriority.HIGH),
        StartFaceTracking(priority=TaskPriority.MID),

        # listen to doorbell

        # drive to door when door bell is detected

        # start looking at person
        GestureFaceFollow(),

        # introduce yourself
        Speak("Hi, my name is Georg."),

        # wave to person? 
        # GestureGreetPerson("right"),

        # listen to name
        Speak("What's your name?"),
        ask_name,
        Remember(store_name),

        # answer to person with name, ask to take bag
        Speak(lambda state: f"Nice to meet you {name or ''}!"),
        
        # offer hand to take bag of guest
        # GestureOfferCloseHand(),

        # ask guest to follow pib to living room
        Speak(lambda state: f"{ name or ''}, please follow me to the living room."),

        # stop looking at person

        # navigate to living room

        # start looking at person

        # introduce guest to host, ask/tell host to take the bag

        # offer hand with bag to host
        # GestureOfferCloseHand(),

        # listen to host about where to find objects

        # stop looking at person

        # look at objects and describe scene
        DescribeScene(),
        Speak(lambda state: state.scene_description),

        # tell guest, which objects are there

        # point at objects?/grasp an object?

        # start looking at person
        
        # listen to guest (who wants to leave again)

        # ask guest to follow him guiding him to the door

        # stop looking at person 

        # navigate to door

        # start looking at person

        # wave goodbye

        # say goodbye

        # stop all tasks

        # stop vision models
        StopFaceTracking(priority=TaskPriority.MID),
        StopObjectDetection(priority=TaskPriority.HIGH),
    ]