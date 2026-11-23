"""Drive to a named place of the map YAML with Nav2 (pkg_nav2, action navigate_to_pose).

    place name -> (x, y) from the map YAML -> stop short by standoff_m -> NavigateToPose

At the goal pib faces the place (tasks/nav2_go.py). The robot's position for standoff and
heading comes from odom (robot.py), which is the map frame in the simulation.
"""

from . import nav2_go
from .base import BaseTask, default_map_path, load_place
from .priority import TaskPriority


class NavigateObject(BaseTask):
    """Navigate to a named object of the map YAML (e.g. a seat or the door)."""

    # stop this far (m) before the object, so the goal is not on/inside it
    DEFAULT_STANDOFF_M = 0.3
    TIMEOUT_S = 180.0

    def __init__(self, object_name: str, map_path: str = None,
                 standoff_m: float = DEFAULT_STANDOFF_M,
                 priority: TaskPriority = TaskPriority.LOW):
        super().__init__("NavigateObject", priority)
        self.object_name = object_name
        # no map given (e.g. by the LLM planner): the current map of this robot
        self.map_path = map_path or default_map_path()
        self.standoff_m = standoff_m

    async def run(self, robot, state):
        print(f"[TASK] {self.name} started -> '{self.object_name}'")
        target = load_place(self.map_path, self.object_name)
        if target is None:
            print(f"[TASK] {self.name} FAILED: '{self.object_name}' not found in map")
            return False
        start = getattr(state, "current_position", None)
        if start is None:
            print(f"[TASK] {self.name} FAILED: no current position available")
            return False

        goal_point = self._apply_standoff(start, target, self.standoff_m)
        state.is_navigating = True
        try:
            ok = await nav2_go.nav2_go(
                robot.nav2_action_client,
                nav2_go.make_goal(*goal_point, nav2_go.facing_yaw(start, target)),
                timeout=self.TIMEOUT_S,
                abort_check=lambda: getattr(state, "abort_requested", False),
            )
        finally:
            state.is_navigating = False
        print(f"[TASK] {self.name} {'finished' if ok else 'FAILED'} -> '{self.object_name}'")
        return ok

    @staticmethod
    def _apply_standoff(start, target, standoff_m):
        """Move the goal ``standoff_m`` towards the start, so the robot does not drive into it."""
        if standoff_m <= 0:
            return target
        dx = target[0] - start[0]
        dy = target[1] - start[1]
        dist = (dx ** 2 + dy ** 2) ** 0.5
        if dist <= standoff_m:
            return start  # already within the standoff distance: do not move
        ratio = (dist - standoff_m) / dist
        return (start[0] + dx * ratio, start[1] + dy * ratio)
