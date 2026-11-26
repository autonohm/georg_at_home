from .base import BaseTask
from .timeout_watcher import wait_for_service_result
from .priority import TaskPriority


class Remember(BaseTask):

    def __init__(self, func, priority: TaskPriority = TaskPriority.LOW):
        super().__init__("Remember", priority)
        self.func = func

    async def run(self, robot, state):
        try:
                self.func(state)
        except Exception as exc:
            print(f"[TASK] Remember: failed:  {exc!r}")
            return False
        return True