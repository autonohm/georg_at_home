from georg_task_manager.tasks.StartFaceTracking import StartFaceTracking
from georg_task_manager.tasks.StopFaceTracking import StopFaceTracking
from georg_task_manager.tasks.priority import TaskPriority
from georg_task_manager.tasks.FaceFollow import GestureFaceFollow # GestureOfferCloseHand, GestureCloseHand, GestureOpenHand, GestureGreetPerson, GestureLookAt, GestureOfferHand, GesturePointTo



def get_mission():
    print("[MISSION] Qualification started")

    return [

        # start vision models
        #StartFaceTracking(priority=TaskPriority.MID),


        # start looking at person
        GestureFaceFollow(),

       
        # stop vision models
        #StopFaceTracking(priority=TaskPriority.MID),
    ]