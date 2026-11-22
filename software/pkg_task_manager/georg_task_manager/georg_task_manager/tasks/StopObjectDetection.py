from .base import BaseTask
from .timeout_watcher import wait_for_service_result
from .priority import TaskPriority
from datatypes.srv import StopModel


class StopObjectDetection(BaseTask):
    def __init__(self, priority=TaskPriority.LOW):
        super().__init__("StopObjectDetection", priority)

    async def run(self, robot, state):
        request = StopModel.Request()
        request.model_id = 'yolov6n_coco_640x640'
        request.shaves = '4' 
        request.owner = 'Taskmanagement'

        response = await wait_for_service_result(
            robot.StopModel,
            request,
            timeout=60.0,
            abort_check=lambda: getattr(state, "abort_requested", False),
        )
        return response is not None