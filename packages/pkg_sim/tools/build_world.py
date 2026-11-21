"""Build Georg's simulation apartment (modelled on the RoboCup@Home arena).

    python3 packages/pkg_sim/tools/build_world.py      # writes pkg_slam/maps/Wohnung.yaml
                                                       # and pkg_slam/maps/Wohnung_visuals.xml

9 x 9 m, four rooms like the arena (living room, office, kitchen, bedroom), closed walls
(1.25 m) with 0.9 m doorways, an entrance, furniture and three people. One description here
gives everything the same geometry:
  Wohnung.yaml          map like Nav_Test.yaml: obstacle polygons (navigation, lidar, physics)
                        and named places (navigation targets, all checked reachable)
  Wohnung_visuals.xml   MJCF snippet for the camera image (boxes with height and colour)

Use it with GEORG_MAP=Wohnung.yaml ./projectctl.bash up sim
"""
import math
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arena_convert import is_free, reachable  # noqa: E402  (geometry helpers, no USD needed)

HERE = os.path.dirname(os.path.abspath(__file__))
MAPS = os.path.join(HERE, '..', '..', 'pkg_slam', 'maps')
SIZE = 9.0
WALL_T = 0.1
WALL_H = 2.4      # full room height (the RoboCup arena has 1.25 m, the camera looked over it)
DOOR = 0.9

WHITE = (0.93, 0.93, 0.9)
WOOD = (0.62, 0.45, 0.3)
DARK = (0.25, 0.25, 0.28)

# walls: (x0, y0, x1, y1) axis-aligned, doorways are gaps (y = 4.5 and x = 4.5 split the rooms)
H, V = SIZE / 2, SIZE / 2


def _wall_x(y, x0, x1, gaps=()):
    """Horizontal wall at y from x0 to x1 with doorway gaps [(a, b), ...]."""
    out, start = [], x0
    for a, b in sorted(gaps):
        out.append((start, y - WALL_T / 2, a, y + WALL_T / 2))
        start = b
    out.append((start, y - WALL_T / 2, x1, y + WALL_T / 2))
    return out


def _wall_y(x, y0, y1, gaps=()):
    out, start = [], y0
    for a, b in sorted(gaps):
        out.append((x - WALL_T / 2, start, x + WALL_T / 2, a))
        start = b
    out.append((x - WALL_T / 2, start, x + WALL_T / 2, y1))
    return out


WALLS = (
    _wall_x(0.0, 0.0, SIZE, gaps=[(1.0, 1.0 + DOOR)])            # south, entrance (kitchen)
    + _wall_x(SIZE, 0.0, SIZE)                                    # north
    + _wall_y(0.0, 0.0, SIZE)                                     # west
    + _wall_y(SIZE, 0.0, SIZE)                                    # east
    + _wall_x(H, 0.0, SIZE, gaps=[(2.0, 2.0 + DOOR), (6.6, 6.6 + DOOR)])   # kitchen|living,
                                                                  # bedroom|office
    + _wall_y(V, 0.0, SIZE, gaps=[(1.9, 1.9 + DOOR), (6.3, 6.3 + DOOR)])   # kitchen|bedroom,
                                                                  # living|office
)

# furniture: name, (x0, y0, x1, y1), height, rgb, place name (navigation target) or None
FURNITURE = [
    # kitchen (bottom left)
    ('Kuehlschrank', (0.1, 0.1, 0.8, 0.8), 1.8, (0.85, 0.87, 0.9), 'Kuehlschrank'),
    ('Kuechenzeile', (2.3, 0.1, 4.4, 0.7), 0.9, (0.55, 0.35, 0.25), 'Spuele'),
    ('Esstisch', (1.5, 2.2, 2.7, 3.2), 0.75, WOOD, 'Esstisch'),
    ('Stuhl_1', (1.8, 1.7, 2.2, 2.1), 0.9, DARK, None),
    ('Stuhl_2', (1.8, 3.3, 2.2, 3.7), 0.9, DARK, None),
    ('Regal_Kueche', (0.1, 3.4, 0.5, 4.4), 1.6, WHITE, None),
    # living room (top left)
    ('Sofa', (0.15, 6.0, 1.05, 8.2), 0.8, (0.35, 0.45, 0.6), 'Sofa'),
    ('Couchtisch', (1.6, 6.6, 2.4, 7.6), 0.45, WOOD, 'Couchtisch'),
    ('Fernseher', (1.5, 8.5, 3.2, 8.9), 0.6, DARK, 'Fernseher'),
    ('Pflanze_Wohnzimmer', (3.95, 8.4, 4.4, 8.9), 1.2, (0.2, 0.55, 0.25), None),
    ('Regal_Wohnzimmer', (3.9, 4.6, 4.4, 5.6), 1.5, WHITE, None),
    # bedroom (bottom right)
    ('Bett', (6.6, 1.2, 8.9, 3.2), 0.55, (0.8, 0.8, 0.85), 'Bett'),
    ('Kleiderschrank', (4.6, 0.1, 6.2, 0.7), 2.0, (0.9, 0.9, 0.88), 'Kleiderschrank'),
    ('Nachttisch', (8.4, 3.3, 8.9, 3.8), 0.5, WOOD, None),
    # office (top right)
    ('Schreibtisch', (7.2, 8.2, 8.9, 8.9), 0.75, WOOD, 'Schreibtisch'),
    ('Buerostuhl', (7.8, 7.5, 8.3, 8.0), 1.0, DARK, None),
    ('Regal_Buero', (4.6, 7.6, 5.1, 8.9), 1.5, WHITE, 'Regal'),
    ('Pflanze_Buero', (8.5, 4.6, 8.9, 5.0), 1.2, (0.2, 0.55, 0.25), None),
]

# people: name, (x, y), place name in front of them
PEOPLE = [
    ('Person_Kueche', (3.4, 2.4), 'Person_Kueche'),
    ('Person_Wohnzimmer', (2.9, 6.2), 'Person_Wohnzimmer'),
    ('Person_Buero', (6.2, 6.0), 'Person_Buero'),
]
PERSON_R = 0.22
PERSON_H = 1.7

EXTRA_PLACES = {'Eingang': (1.45, 0.75), 'Flur_Wohnzimmer': (2.45, 5.2),
                'Flur_Buero': (5.2, 6.75), 'Flur_Schlafzimmer': (5.2, 2.35)}
START = (2.45, 4.0)


def _rect(b):
    x0, y0, x1, y1 = b
    return [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]


def _octagon(c, r):
    return [[c[0] + r * math.cos(k * math.pi / 4), c[1] + r * math.sin(k * math.pi / 4)]
            for k in range(8)]


def _round(points):
    return [[round(x, 3), round(y, 3)] for x, y in points]


def _place_near(box, polygons, radius=0.4):
    """Free spot on the side of a box facing open floor, as close as possible."""
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    for clearance in [c / 10 for c in range(4, 21)]:
        for q in ((x1 + clearance, cy), (x0 - clearance, cy), (cx, y1 + clearance),
                  (cx, y0 - clearance)):
            if 0.3 < q[0] < SIZE - 0.3 and 0.3 < q[1] < SIZE - 0.3 and \
                    is_free(q[0], q[1], polygons, radius):
                return q
    raise RuntimeError(f'no free spot next to {box}')


def build():
    """Return (map dict, visuals XML)."""
    polygons, geoms = [], []
    for i, b in enumerate(WALLS):
        polygons.append({'name': f'Wand_{i}', 'type': 'obstacle', 'frame': 'map',
                         'color': 'black', 'points': _round(_rect(b))})
        geoms.append(_box(f'Wand_{i}', b, WALL_H, WHITE))
    for name, b, h, rgb, _ in FURNITURE:
        polygons.append({'name': name, 'type': 'obstacle', 'frame': 'map', 'color': 'red',
                         'points': _round(_rect(b))})
        geoms.append(_box(name, b, h, rgb))
    # ceiling and one light per room (the ceiling blocks the light from above)
    geoms.append(f'<geom name="v_Decke" type="box" pos="{SIZE / 2} {SIZE / 2} {WALL_H + 0.03}" '
                 f'size="{SIZE / 2} {SIZE / 2} 0.03" rgba="0.97 0.97 0.95 1" contype="0" '
                 'conaffinity="0" group="1"/>')
    for x in (SIZE / 4, 3 * SIZE / 4):
        for y in (SIZE / 4, 3 * SIZE / 4):
            geoms.append(f'<light pos="{x} {y} {WALL_H - 0.1}" dir="0 0 -1" '
                         'diffuse="0.45 0.45 0.42" attenuation="1 0.05 0" castshadow="false"/>')
    for name, c, _ in PEOPLE:
        polygons.append({'name': name, 'type': 'obstacle', 'frame': 'map', 'color': 'purple',
                         'points': _round(_octagon(c, PERSON_R))})
        geoms += _person(name, c)

    polys = [p['points'] for p in polygons]
    places = {}
    for name, b, _, _, place in FURNITURE:
        if place:
            places[place] = _place_near(b, polys)
    for name, c, place in PEOPLE:
        places[place] = _place_near((c[0] - PERSON_R, c[1] - PERSON_R,
                                     c[0] + PERSON_R, c[1] + PERSON_R), polys, radius=0.4)
    places.update(EXTRA_PLACES)
    places['Mitte'] = START
    for name, q in places.items():
        if not is_free(q[0], q[1], polys, 0.3):
            raise RuntimeError(f'place {name} {q} is not free')
    import numpy as np
    ok = reachable(START, places, polys, np.array([0.0, 0.0]), np.array([SIZE, SIZE]))
    bad = [n for n, r in ok.items() if not r]
    if bad:
        raise RuntimeError(f'not reachable from the start: {bad}')

    objects = {n: {'type': 'place', 'frame': 'map', 'position': [round(q[0], 3), round(q[1], 3)]}
               for n, q in places.items()}
    objects['Start'] = {'type': 'sim_start', 'frame': 'map', 'position': list(START)}
    doc = {
        'map': {'resolution': 0.05, 'origin': [-0.3, -0.3], 'width_px': 192, 'height_px': 192,
                'width_m': 9.6, 'height_m': 9.6,
                'source': 'pkg_sim/tools/build_world.py (modelled on the RoboCup@Home arena)'},
        'objects': objects,
        'polygons': polygons + [{'name': 'Arena', 'type': 'boundary', 'frame': 'map',
                                 'color': 'orange',
                                 'points': _round(_rect((-0.3, -0.3, SIZE + 0.3, SIZE + 0.3)))}],
    }
    xml = ('<mujocoinclude>\n  <asset>\n  </asset>\n  <worldbody>\n    ' + '\n    '.join(geoms)
           + '\n  </worldbody>\n</mujocoinclude>\n')
    return doc, xml


def _box(name, b, h, rgb):
    x0, y0, x1, y1 = b
    r, g, bl = rgb
    return (f'<geom name="v_{name}" type="box" pos="{(x0 + x1) / 2:.3f} {(y0 + y1) / 2:.3f} '
            f'{h / 2:.3f}" size="{(x1 - x0) / 2:.3f} {(y1 - y0) / 2:.3f} {h / 2:.3f}" '
            f'rgba="{r} {g} {bl} 1" contype="0" conaffinity="0" group="1"/>')


def _person(name, c):
    x, y = c
    body = 1.25
    return [
        f'<geom name="v_{name}_body" type="capsule" fromto="{x} {y} 0.15 {x} {y} {body}" '
        f'size="{PERSON_R * 0.9:.3f}" rgba="0.2 0.3 0.55 1" contype="0" conaffinity="0"/>',
        f'<geom name="v_{name}_head" type="sphere" pos="{x} {y} {PERSON_H - 0.12}" size="0.12" '
        'rgba="0.95 0.78 0.65 1" contype="0" conaffinity="0"/>',
    ]


def main():
    """Write the map and the visuals."""
    doc, xml = build()
    path = os.path.join(MAPS, 'Wohnung.yaml')
    with open(path, 'w', encoding='utf-8') as f:
        f.write('# Generated by pkg_sim/tools/build_world.py - edit the script, not this file.\n'
                '# Simulation apartment modelled on the RoboCup@Home arena (9 x 9 m, 4 rooms).\n')
        yaml.safe_dump(doc, f, sort_keys=False, allow_unicode=True)
    with open(os.path.join(MAPS, 'Wohnung_visuals.xml'), 'w', encoding='utf-8') as f:
        f.write(xml)
    print(f'{path}: {len(doc["polygons"])} polygons, places: {", ".join(doc["objects"])}')


if __name__ == '__main__':
    main()
