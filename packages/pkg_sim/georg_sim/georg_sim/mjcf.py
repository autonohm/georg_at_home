"""MuJoCo model (MJCF) of Georg's base in a world built from a map YAML (P3, stage 2).

No MuJoCo import in here, so the XML can be checked without MuJoCo installed.

- every wall segment of the map becomes a box (0.05 m thick, 0.5 m high)
- the robot is a cylinder that moves in the plane: slide joints x/y and a hinge for yaw,
  each driven by a velocity actuator (a simple stand-in for the mecanum wheels)
- the floor does not collide with anything (the robot has no z joint)

The model of the real robot (pkg_urdf) can replace the cylinder later; the joint and
actuator names (x, y, yaw / vx, vy, wz) are what the simulator node drives.
"""

import math
from typing import Iterable
from xml.sax.saxutils import quoteattr

from georg_sim.world import Segment, World

WALL_THICKNESS = 0.05
WALL_HEIGHT = 0.5


def _wall(i: int, seg: Segment) -> str:
    (x1, y1), (x2, y2) = seg
    length = math.hypot(x2 - x1, y2 - y1)
    if length < 1e-6:
        return ''
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    yaw = math.atan2(y2 - y1, x2 - x1)
    return (f'<geom name="wall{i}" type="box" pos="{cx:.4f} {cy:.4f} {WALL_HEIGHT / 2}" '
            f'euler="0 0 {yaw:.6f}" size="{length / 2:.4f} {WALL_THICKNESS / 2} '
            f'{WALL_HEIGHT / 2}" rgba="0.6 0.6 0.65 1"/>')


def build_mjcf(world: World, start=(1.0, 0.1, 0.0), radius: float = 0.2,
               segments: Iterable[Segment] = None) -> str:
    """Return the MJCF XML of the arena and the robot."""
    boxes = (_wall(i, s) for i, s in enumerate(segments or world.segments))
    walls = '\n    '.join(w for w in boxes if w)
    x, y, yaw = start
    name = quoteattr('georg')
    return f"""<mujoco model={name}>
  <compiler angle="radian"/>
  <option timestep="0.002" gravity="0 0 -9.81"/>
  <default>
    <geom friction="0.5 0.005 0.0001"/>
  </default>
  <worldbody>
    <geom name="floor" type="plane" size="20 20 0.1" contype="0" conaffinity="0"
          rgba="0.9 0.9 0.9 1"/>
    {walls}
    <body name="base" pos="0 0 0.15">
      <joint name="x" type="slide" axis="1 0 0" ref="0" damping="1"/>
      <joint name="y" type="slide" axis="0 1 0" ref="0" damping="1"/>
      <joint name="yaw" type="hinge" axis="0 0 1" damping="1"/>
      <geom name="base" type="cylinder" size="{radius} 0.15" mass="25" rgba="0.2 0.4 0.8 1"/>
      <site name="lidar" pos="0 0 0.1"/>
    </body>
  </worldbody>
  <actuator>
    <velocity name="vx" joint="x" kv="400" ctrlrange="-2 2"/>
    <velocity name="vy" joint="y" kv="400" ctrlrange="-2 2"/>
    <velocity name="wz" joint="yaw" kv="60" ctrlrange="-4 4"/>
  </actuator>
  <keyframe>
    <key name="start" qpos="{x} {y} {yaw}"/>
  </keyframe>
</mujoco>
"""
