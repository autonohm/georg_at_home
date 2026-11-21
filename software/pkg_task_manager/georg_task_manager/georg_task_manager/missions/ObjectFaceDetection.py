from georg_task_manager.tasks.StartFaceTracking import StartFaceTracking
from georg_task_manager.tasks.StopFaceTracking import StopFaceTracking
from georg_task_manager.tasks.StartObjectDetection import StartObjectDetection
from georg_task_manager.tasks.StopObjectDetection import StopObjectDetection

def get_mission():
    return [Speak("Hallo, ich bin Georg.")]