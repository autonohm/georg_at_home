import asyncio
import os

from .priority import TaskPriority


def default_map_path() -> str:
    """Map of this robot: GEORG_MAP_DIR/GEORG_DEFAULT_MAP (default /root/georg_maps/Nav_Test.yaml)."""
    return os.path.join(os.environ.get('GEORG_MAP_DIR', '/root/georg_maps'),
                        os.environ.get('GEORG_DEFAULT_MAP', 'Nav_Test.yaml'))


class BaseTask:

    def __init__(self, name, priority: TaskPriority = TaskPriority.LOW):
        self.name = name
        self.priority = priority
        self.attempts = 0

    async def run(self, interface):
        raise NotImplementedError