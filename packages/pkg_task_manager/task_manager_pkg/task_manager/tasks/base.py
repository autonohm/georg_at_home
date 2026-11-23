import asyncio
import os

from .priority import TaskPriority


# world chosen at runtime (sim: /sim/world from the simulator), wins over GEORG_DEFAULT_MAP
_current_map = None


def set_default_map(name) -> None:
    """Use map ``name`` (file name in GEORG_MAP_DIR) from now on; None: back to the env."""
    global _current_map
    _current_map = name or None


def default_map_path() -> str:
    """Map of this robot: GEORG_MAP_DIR/<map> (default /root/georg_maps/Nav_Test.yaml).

    <map> is the world of the simulator if it was switched (set_default_map), else
    GEORG_DEFAULT_MAP.
    """
    name = _current_map or os.environ.get('GEORG_DEFAULT_MAP', 'Nav_Test.yaml')
    return os.path.join(os.environ.get('GEORG_MAP_DIR', '/root/georg_maps'),
                        os.path.basename(name))


def load_place(map_path: str, name: str):
    """(x, y) of object ``name`` in the map YAML, or None if the map has no such object."""
    import yaml
    with open(map_path, encoding='utf-8') as f:
        data = yaml.safe_load(f) or {}
    obj = (data.get('objects') or {}).get(name)
    if obj is None:
        return None
    pos = obj['position']
    return float(pos[0]), float(pos[1])


class BaseTask:

    def __init__(self, name, priority: TaskPriority = TaskPriority.LOW):
        self.name = name
        self.priority = priority
        self.attempts = 0

    async def run(self, interface):
        raise NotImplementedError