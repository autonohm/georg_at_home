"""Lets the Burr tests run without ROS.

If a ROS module is not importable (e.g. on a laptop), a stand-in module is
put into sys.modules. Inside the container the real modules are used.
"""

import importlib
import os
import sys
import types
from unittest.mock import MagicMock

PKG_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PKG_ROOT not in sys.path:
    sys.path.insert(0, PKG_ROOT)

ROS_MODULES = [
    "rclpy", "rclpy._rclpy_pybind11", "rclpy.node", "rclpy.action",
    "std_msgs", "std_msgs.msg",
    "geometry_msgs", "geometry_msgs.msg",
    "nav_msgs", "nav_msgs.msg",
    "datatypes", "datatypes.action",
    "georg_gesture_msgs", "georg_gesture_msgs.action",
    "georg_nav_msgs", "georg_nav_msgs.action",
    "navigate_server", "navigate_server.grid_rasterizer",
]


def _stub(name):
    module = types.ModuleType(name)
    module.__getattr__ = lambda attr: MagicMock(name=f"{name}.{attr}")
    return module


STUBBED = set()

for _name in ROS_MODULES:
    try:
        importlib.import_module(_name)
    except Exception:
        sys.modules[_name] = _stub(_name)
        STUBBED.add(_name)
        parent, _, child = _name.rpartition(".")
        if parent and parent in sys.modules:
            setattr(sys.modules[parent], child, sys.modules[_name])

# rclpy stub: not initialised, so publishing is skipped like in a stopped node
if "rclpy" in STUBBED:
    sys.modules["rclpy"].ok = lambda: False
    sys.modules["rclpy._rclpy_pybind11"].RCLError = RuntimeError
