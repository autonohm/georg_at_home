"""Drive into a named room of the map YAML with Nav2: the room's point, no standoff."""

from .NavigateObject import NavigateObject
from .priority import TaskPriority


class NavigateRoom(NavigateObject):
    """Navigate to the point of a room (an object of the map YAML)."""

    def __init__(self, room_name: str, map_path: str = None,
                 priority: TaskPriority = TaskPriority.LOW):
        super().__init__(room_name, map_path, standoff_m=0.0, priority=priority)
        self.name = "NavigateRoom"
        self.room_name = room_name
