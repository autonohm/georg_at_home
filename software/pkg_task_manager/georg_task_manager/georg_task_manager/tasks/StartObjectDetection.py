from .base import BaseTask
from .timeout_watcher import wait_for_service_result
from .priority import TaskPriority
from datatypes.srv import StartModel
from datatypes.srv import StopModel


class StartObjectDetection(BaseTask):
    def __init__(self, priority=TaskPriority.LOW):
        super().__init__("StartObjectDetection", priority)

    async def run(self, robot, state):
        request = StartModel.Request()
        request.model_id = 'yolov6n_coco_640x640'
        request.shaves = '4' 
        request.owner = 'Taskmanagement'

        response = await wait_for_service_result(
            robot.StartModel,
            request,
            timeout=60.0,
            abort_check=lambda: getattr(state, "abort_requested", False),
        )
        return response is not None