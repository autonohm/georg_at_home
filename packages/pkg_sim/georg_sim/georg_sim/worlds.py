"""Worlds of the simulation: the map YAMLs in GEORG_MAP_DIR and their camera visuals.

A world is a map YAML (pkg_slam/maps) with walls/obstacles; optional ``<name>_visuals.xml``
next to it holds furniture meshes for the camera (pkg_sim/tools). Switching the world at
runtime: publish the file name on ``/sim/set_world`` (std_msgs/String), e.g. from the
Lichtblick panel; the simulator publishes the current world on ``/sim/world`` and the
choices on ``/sim/worlds`` (JSON list), both latched.
"""

import json
import os

# converted RoboCup@Home arena: meshes are generated and mounted separately (not in git)
SPECIAL_VISUALS = {'Arena_AtHome.yaml': '/root/arena/arena_visuals.xml'}


def list_worlds(map_dir):
    """Map YAMLs that describe a world (have polygons), sorted by name."""
    names = []
    try:
        entries = sorted(os.listdir(map_dir))
    except OSError:
        return names
    for name in entries:
        if not name.endswith('.yaml'):
            continue
        try:
            with open(os.path.join(map_dir, name), encoding='utf-8') as fh:
                if 'polygons:' in fh.read():
                    names.append(name)
        except OSError:
            continue
    return names


def resolve(name, map_dir):
    """Absolute path of world ``name`` (file name or path), or None if it is not a world."""
    name = os.path.basename(str(name).strip())
    if name and not name.endswith('.yaml'):
        name += '.yaml'
    return os.path.join(map_dir, name) if name in list_worlds(map_dir) else None


def visuals_for(map_file):
    """Camera visuals of a map: ``<map>_visuals.xml`` next to it, special cases, or ''."""
    special = SPECIAL_VISUALS.get(os.path.basename(map_file))
    if special:
        return special if os.path.exists(special) else ''
    path = map_file[:-len('.yaml')] + '_visuals.xml' if map_file.endswith('.yaml') else ''
    return path if path and os.path.exists(path) else ''


def worlds_json(map_dir):
    return json.dumps(list_worlds(map_dir))
