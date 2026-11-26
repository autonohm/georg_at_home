from georg_task_manager.tasks.greet_person import GestureGreetPerson
from georg_task_manager.tasks.priority import TaskPriority


def get_mission():
    print("Mission greet person V2 on started.")
    return [
        GestureGreetPerson("right", priority=TaskPriority.LOW)
    ]