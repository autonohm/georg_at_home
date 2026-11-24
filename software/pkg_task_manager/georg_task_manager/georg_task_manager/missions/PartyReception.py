from georg_task_manager.tasks.Speak import Speak
from georg_task_manager.tasks.StartFaceTracking import StartFaceTracking
from georg_task_manager.tasks.StopFaceTracking import StopFaceTracking
from georg_task_manager.tasks.StartObjectDetection import StartObjectDetection
from georg_task_manager.tasks.StopObjectDetection import StopObjectDetection
from georg_task_manager.tasks.priority import TaskPriority



def get_mission():
    print("[MISSION] Qualification started")
    return [
        # listen to doorbell

        # drive to door when door bell is detected

        # start looking at person
        StartFaceTracking(priority=TaskPriority.MID),

        # introduce yourself
        Speak("Hallo, ich bin Geeeorg, meine Freunde nennen mich Schorsch."),
        Speak("Wie ist dein Name?"),

        # wave to person? 

        # listen to name

        # answer to person with name, ask to take bag
        
        # offer hand to take bag of guest

        # ask guest to follow pib to living room

        # stop looking at person

        # navigate to living room

        # start looking at person

        # introduce guest to host, ask/tell host to take the bag

        # offer hand with bag to host

        # listen to host about where to find objects

        # stop looking at person

        # look at objects
        # StopFaceTracking(priority=TaskPriority.MID),
        StartObjectDetection(priority=TaskPriority.HIGH),

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