"""2D world from a map YAML (same format as pkg_slam/maps): walls as line segments.

No ROS in here, so it can be tested with plain pytest.

- ``boundary`` polygon: the arena edge; outside is blocked
- ``obstacle`` polygon: solid
- any other polygon type: only its edges block (thin wall)
"""

import math
from typing import List, Tuple

import yaml

Point = Tuple[float, float]
Segment = Tuple[Point, Point]


def _edges(points: List[Point]) -> List[Segment]:
    return [(points[i], points[(i + 1) % len(points)]) for i in range(len(points))]


def _inside(p: Point, poly: List[Point]) -> bool:
    """Even-odd rule."""
    x, y = p
    inside = False
    for (x1, y1), (x2, y2) in _edges(poly):
        if (y1 > y) != (y2 > y):
            if x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                inside = not inside
    return inside


def _dist_point_segment(p: Point, seg: Segment) -> float:
    (x, y), ((x1, y1), (x2, y2)) = p, seg
    dx, dy = x2 - x1, y2 - y1
    length2 = dx * dx + dy * dy
    t = 0.0 if length2 == 0 else max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) / length2))
    return math.hypot(x - (x1 + t * dx), y - (y1 + t * dy))


class World:

    def __init__(self, boundary: List[Point], solids: List[List[Point]],
                 walls: List[List[Point]], objects: dict):
        self.boundary = boundary
        self.solids = solids
        self.walls = walls
        self.objects = objects
        self.segments: List[Segment] = []
        for poly in ([boundary] if boundary else []) + solids + walls:
            self.segments += _edges(poly)

    @classmethod
    def from_yaml(cls, path: str) -> 'World':
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        boundary, solids, walls = [], [], []
        for poly in data.get('polygons') or []:
            pts = [(float(p[0]), float(p[1])) for p in poly.get('points') or []]
            if len(pts) < 2:
                continue
            kind = poly.get('type', '')
            if kind == 'boundary':
                boundary = pts
            elif kind == 'obstacle':
                solids.append(pts)
            else:
                walls.append(pts)
        objects = {name: tuple(o['position'][:2]) for name, o in
                   (data.get('objects') or {}).items() if 'position' in o}
        return cls(boundary, solids, walls, objects)

    def is_free(self, p: Point, radius: float = 0.0) -> bool:
        """Check that a disc of ``radius`` at ``p`` touches no wall and lies inside the arena."""
        if self.boundary and not _inside(p, self.boundary):
            return False
        if any(_inside(p, poly) for poly in self.solids):
            return False
        return all(_dist_point_segment(p, s) > radius for s in self.segments)

    def raycast(self, origin: Point, angle: float, max_range: float) -> float:
        """Distance to the first wall along ``angle``, or ``inf`` beyond ``max_range``."""
        ox, oy = origin
        dx, dy = math.cos(angle), math.sin(angle)
        best = math.inf
        for (x1, y1), (x2, y2) in self.segments:
            sx, sy = x2 - x1, y2 - y1
            denom = dx * sy - dy * sx
            if abs(denom) < 1e-12:
                continue
            qx, qy = x1 - ox, y1 - oy
            t = (qx * sy - qy * sx) / denom      # along the ray
            u = (qx * dy - qy * dx) / denom      # along the segment
            if t > 0.0 and 0.0 <= u <= 1.0 and t < best:
                best = t
        return best if best <= max_range else math.inf

    def scan(self, x: float, y: float, yaw: float, n: int, max_range: float) -> List[float]:
        """Scan 360 degrees with ``n`` beams from -pi to +pi relative to ``yaw``."""
        step = 2 * math.pi / n
        return [self.raycast((x, y), yaw - math.pi + i * step, max_range) for i in range(n)]
