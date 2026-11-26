from .base import BaseTask
from .timeout_watcher import wait_for_service_result
from .priority import TaskPriority
from datatypes.srv import StopModel


class StopFaceTracking(BaseTask):
    def __init__(self, priority=TaskPriority.LOW):
        super().__init__("StopFaceTracking", priority)

    async def run(self, robot, state):
        request = StopModel.Request()
        request.model_id = 'face_detection_yunet_160x120'
        request.owner = 'Taskmanagement'

        response = await wait_for_service_result(
            robot.StopModel,
            request,
            timeout=60.0,
            abort_check=lambda: getattr(state, "abort_requested", False),
        )
        return response is not None