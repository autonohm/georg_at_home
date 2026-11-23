from georg_task_manager.tasks.StartFaceTracking import StartFaceTracking
from georg_task_manager.tasks.StopFaceTracking import StopFaceTracking
from georg_task_manager.tasks.StartObjectDetection import StartObjectDetection
from georg_task_manager.tasks.StopObjectDetection import StopObjectDetection
from georg_task_manager.tasks.priority import TaskPriority


def get_mission():
    print("Mission vision off started.")
    return [
        StopObjectDetection(priority=TaskPriority.HIGH),
        StopFaceTracking(priority=TaskPriority.HIGH),
    ]