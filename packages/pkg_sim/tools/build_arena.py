"""Build the independent, original Georg arena (metres, Z up).

    python3 packages/pkg_sim/tools/build_arena.py
    python3 -m pytest packages/pkg_sim/test/test_arena.py
    GEORG_MAP=Arena.yaml ./projectctl.bash up sim

Dependencies: PyYAML; tests additionally need numpy, pytest and MuJoCo 3.16.
Use dev/macos/.pixi/envs/default/bin/python on the development Mac.
No USD/Blend geometry or external assets are used. All shapes, including the
small OBJ meshes, are constructed here. The reference apartment supplies
only the 9 x 9 m, four-room concept and furniture categories. Layout is adapted
to Georg's 0.35 m base radius, with 1.4 m openings and fully open door leaves.

Furniture polygons conservatively cover every component below 1 m, including
tabletops, arms and door handles. Decorative floors are not obstacles. Door
lintels start at 2.12 m. Standpoints are explicit, on the usable furniture side;
tests check the saved files, independently of the generator.

Tabletop props are separate named bodies, with bottom-centred local frames.
Arena.yaml's optional scene_objects section records their initial poses and
supports separately from the 2D navigation places. Bottle grasp sites are hidden
geometric references in the cylindrical body, NOT validated robot grasp poses.
All props are still static camera geometry with collisions disabled, per the
visuals contract. Actual lifting needs a future physics scene with free joints,
mass/inertia, collision shapes, support contacts and Georg's arm/gripper model;
the camera must then follow those dynamic object poses. No grasp controller or
successful grasp is implied by these references.

The unchanged camera loader discovers Arena_visuals.xml from GEORG_MAP.
For stack regression use Nav_Test, as tests/stack/run.sh sim assumes that map.
The arena_tour mission belongs to the task-manager integration handoff; this
generator deliberately only writes the files permitted by CODEX_ARENA.md.
"""

import argparse
import math
from pathlib import Path
import xml.etree.ElementTree as ET

import yaml

MAPS = Path(__file__).resolve().parents[2] / 'pkg_slam' / 'maps'
WALL_HEIGHT = 2.4
DOOR_WIDTH = 1.4
RESOLUTION = 0.05
START = (3.2, 3.65)

COLORS = {
    'plaster': '0.89 0.88 0.82 1', 'trim': '0.96 0.95 0.91 1',
    'oak': '0.53 0.31 0.16 1', 'lightwood': '0.76 0.57 0.36 1',
    'dark': '0.085 0.105 0.12 1', 'metal': '0.55 0.59 0.61 1',
    'white': '0.93 0.93 0.90 1', 'blue': '0.19 0.36 0.47 1',
    'sage': '0.41 0.56 0.46 1', 'clay': '0.63 0.29 0.17 1',
    'green': '0.16 0.36 0.17 1', 'skin': '0.75 0.49 0.31 1',
    'hair': '0.12 0.075 0.045 1', 'linen': '0.80 0.75 0.62 1',
    'screen': '0.10 0.22 0.28 1', 'yellow': '0.93 0.66 0.20 1',
}


def numbers(values):
    return ' '.join(f'{v:.6g}' for v in values)


def rectangle(bounds):
    x0, y0, x1, y1 = bounds
    return [[round(x0, 5), round(y0, 5)], [round(x1, 5), round(y0, 5)],
            [round(x1, 5), round(y1, 5)], [round(x0, 5), round(y1, 5)]]


def original_meshes():
    """Closed, outward-wound unit sphere and cylinder; no third-party input."""
    n, rings = 16, 8
    vertices = [(0., 0., 1.)]
    for j in range(1, rings):
        theta = math.pi * j / rings
        vertices.extend((math.sin(theta) * math.cos(2 * math.pi * i / n),
                         math.sin(theta) * math.sin(2 * math.pi * i / n), math.cos(theta))
                        for i in range(n))
    vertices.append((0., 0., -1.))
    faces = []
    for i in range(n):
        nxt = (i + 1) % n
        faces.append((0, 1 + i, 1 + nxt))
        for j in range(rings - 2):
            a, b = 1 + j * n + i, 1 + j * n + nxt
            faces.extend(((a, a + n, b), (b, a + n, b + n)))
        a, b = 1 + (rings - 2) * n + i, 1 + (rings - 2) * n + nxt
        faces.append((a, len(vertices) - 1, b))

    def obj(verts, tris, smooth=False):
        lines = ['# Original procedural geometry: build_arena.py; no external assets.']
        lines += ['v ' + numbers(v) for v in verts]
        if smooth:
            lines += ['vn ' + numbers(v) for v in verts]
        for tri in tris:
            lines.append('f ' + ' '.join(f'{i + 1}//{i + 1}' if smooth else str(i + 1)
                                         for i in tri))
        return '\n'.join(lines) + '\n'

    sphere = obj(vertices, faces, smooth=True)
    vertices = [(math.cos(i * 2 * math.pi / n), math.sin(i * 2 * math.pi / n), z)
                for z in (-1., 1.) for i in range(n)] + [(0., 0., -1.), (0., 0., 1.)]
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces.extend(((i, j, i + n), (j, j + n, i + n),
                      (2 * n, j, i), (2 * n + 1, i + n, j + n)))
    cylinder = obj(vertices, faces)

    def lathe(profile):
        # Closed surface of revolution. An inward/downward profile also creates
        # a hollow cup with a real interior, instead of a solid drinking vessel.
        verts = [(r * math.cos(i * 2 * math.pi / n),
                  r * math.sin(i * 2 * math.pi / n), z)
                 for z, r in profile for i in range(n)]
        tris = []
        for row in range(len(profile) - 1):
            for i in range(n):
                a, b = row * n + i, row * n + (i + 1) % n
                tris.extend(((a, b, a + n), (b, b + n, a + n)))
        bottom, top = len(verts), len(verts) + 1
        verts.extend(((0, 0, profile[0][0]), (0, 0, profile[-1][0])))
        last = (len(profile) - 1) * n
        for i in range(n):
            j = (i + 1) % n
            tris.extend(((bottom, j, i), (top, last + i, last + j)))
        return obj(verts, tris)

    bottle = lathe([(0, .88), (.025, 1), (.68, 1), (.82, .45), (1, .45)])
    cup = lathe([(0, .88), (.05, 1), (1, 1), (1, .83), (.13, .83)])
    return {'sphere.obj': sphere, 'cylinder.obj': cylinder,
            'bottle.obj': bottle, 'cup.obj': cup}


class Scene:
    def __init__(self):
        self.root = ET.Element('mujocoinclude')
        self.assets = ET.SubElement(self.root, 'asset')
        self.world = ET.SubElement(self.root, 'worldbody')
        self.polygons = []
        self.props = {}
        self.meshes = {}
        self.count = 0
        for name, rgba in COLORS.items():
            ET.SubElement(self.assets, 'material', name='arena_' + name, rgba=rgba,
                          specular='0.15', shininess='0.2')
        ET.SubElement(self.assets, 'texture', name='arena_tiles', type='2d',
                      builtin='checker', rgb1='0.68 0.70 0.66', rgb2='0.81 0.82 0.77',
                      width='128', height='128')
        ET.SubElement(self.assets, 'material', name='arena_tile_floor',
                      texture='arena_tiles', texrepeat='9 9', reflectance='0')

    def obstacle(self, name, bounds, color='red'):
        self.polygons.append(dict(name=name, type='obstacle', frame='map',
                                  color=color, points=rectangle(bounds)))

    def geom(self, parent, kind, pos, size, material):
        self.count += 1
        attrs = dict(name=f'arena_geom_{self.count}', pos=numbers(pos),
                     material='arena_' + material, contype='0', conaffinity='0', group='1')
        if kind == 'box':
            attrs.update(type='box', size=numbers(size))
        else:
            key = (kind, tuple(size))
            if key not in self.meshes:
                name = f'arena_mesh_{len(self.meshes)}'
                ET.SubElement(self.assets, 'mesh', name=name,
                              file=f'arena_meshes/{kind}.obj', scale=numbers(size))
                self.meshes[key] = name
            attrs.update(type='mesh', mesh=self.meshes[key])
        return ET.SubElement(parent, 'geom', **attrs)

    def box(self, parent, pos, dimensions, material):
        return self.geom(parent, 'box', pos, [v / 2 for v in dimensions], material)

    def item(self, name, center, dimensions, yaw=0):
        """Local furniture frame; footprint contains the rotated rectangular bounds."""
        x, y = center
        w, d = dimensions
        angle = math.radians(yaw)
        hx = (abs(math.cos(angle)) * w + abs(math.sin(angle)) * d) / 2
        hy = (abs(math.sin(angle)) * w + abs(math.cos(angle)) * d) / 2
        self.obstacle(name, (x - hx, y - hy, x + hx, y + hy),
                      'purple' if name.startswith('Person_') else 'red')
        return ET.SubElement(self.world, 'body', name='arena_' + name, pos=f'{x} {y} 0',
                             quat=numbers((math.cos(angle / 2), 0, 0, math.sin(angle / 2))))

    def prop(self, name, category, support, position):
        """A separate static object, already inside its support's map footprint."""
        body_name = 'arena_' + name
        self.props[name] = dict(category=category, body=body_name, support=support,
                                frame='map', position=list(position),
                                simulation='static_visual')
        return ET.SubElement(self.world, 'body', name=body_name, pos=numbers(position))


def architecture(s):
    # Each gap is 1.4 m wide before a 2 cm frame on either side (1.36 m clear).
    horizontal = [(0, [(0, .9), (2.3, 9)]), (9, [(0, 9)]),
                  (4.5, [(0, 2.5), (3.9, 5.1), (6.5, 9)])]
    vertical = [(0, [(0, 9)]), (9, [(0, 9)]),
                (4.5, [(0, 2.8), (4.2, 5.1), (6.5, 9)])]
    index = 0
    for axis, walls in [('x', horizontal), ('y', vertical)]:
        for at, spans in walls:
            for a, b in spans:
                bounds = (a, at - .06, b, at + .06) if axis == 'x' else (at - .06, a, at + .06, b)
                s.obstacle(f'Wand_{index}', bounds, 'black')
                x0, y0, x1, y1 = bounds
                s.box(s.world, ((x0 + x1) / 2, (y0 + y1) / 2, 1.2),
                      (x1 - x0, y1 - y0, WALL_HEIGHT), 'plaster')
                index += 1
    # Open leaves stay alongside walls. Frames and handles are also mapped.
    doors = [('Eingang', 'x', 0., .9), ('Wohnzimmer', 'x', 4.5, 2.5),
             ('Buero', 'x', 4.5, 5.1), ('Schlafzimmer', 'y', 4.5, 2.8),
             ('Wohnzimmer_Buero', 'y', 4.5, 5.1)]
    for name, axis, at, a in doors:
        def location(u, v, z):
            return (u, v, z) if axis == 'x' else (v, u, z)

        def dims(u, v, z):
            return (u, v, z) if axis == 'x' else (v, u, z)

        for side in (a + .01, a + DOOR_WIDTH - .01):
            x, y, z = location(side, at, 1.06)
            w, d, h = dims(.02, .14, 2.12)
            s.obstacle(f'Tuerrahmen_{name}_{side}', (x - w / 2, y - d / 2, x + w / 2, y + d / 2))
            s.box(s.world, (x, y, z), (w, d, h), 'trim')
        s.box(s.world, location(a + .7, at, 2.26), dims(1.4, .12, .28), 'plaster')
        s.box(s.world, location(a + .7, at, 2.1), dims(1.4, .15, .04), 'trim')
        # Leaf folded through 180 degrees against the preceding wall segment.
        # The entrance leaf is shorter, like a double door, so it stays inside 9 m.
        length = .76 if name in ('Eingang', 'Wohnzimmer_Buero') else 1.25
        x, y, _ = location(a - length / 2 - .03, at + .11, 0)
        w, d, _ = dims(length, .08, 0)
        leaf = s.item('Tuer_' + name, (x, y), (w, d))
        s.box(leaf, (0, 0, 1.05), (w, d, 2.1), 'lightwood')
        # Handle stays inside the conservative footprint.
        s.box(leaf, (0, 0, .98), (min(w, .12), min(d, .12), .035), 'metal')

    floors = [('Kueche', (2.25, 2.25), 'tile_floor'),
              ('Wohnzimmer', (2.25, 6.75), 'lightwood'),
              ('Schlafzimmer', (6.75, 2.25), 'linen'),
              ('Buero', (6.75, 6.75), 'sage')]
    for name, (x, y), mat in floors:
        floor = s.box(s.world, (x, y, -.012), (4.5, 4.5, .03), mat)
        floor.set('name', 'arena_floor_' + name)
        ET.SubElement(s.world, 'light', name='arena_light_' + name, pos=f'{x} {y} 2.28',
                      dir='0 0 -1', diffuse='.55 .52 .47', ambient='.12 .12 .12',
                      attenuation='1 .04 .01', castshadow='false')
    ceiling = s.box(s.world, (4.5, 4.5, 2.44), (9, 9, .08), 'trim')
    ceiling.set('name', 'arena_ceiling')


def table(s, name, center, w, d, height):
    body = s.item(name, center, (w, d))
    s.box(body, (0, 0, height - .04), (w, d, .08), 'lightwood')
    for x in (-w / 2 + .07, w / 2 - .07):
        for y in (-d / 2 + .07, d / 2 - .07):
            s.box(body, (x, y, (height - .08) / 2), (.07, .07, height - .08), 'oak')
    return body


def chair(s, name, center, yaw=0):
    body = s.item(name, center, (.46, .48), yaw)
    chair_parts(s, body)
    return body


def chair_parts(s, body):
    s.box(body, (0, 0, .45), (.46, .46, .08), 'blue')
    s.box(body, (0, -.2, .73), (.46, .06, .50), 'blue')
    for x in (-.18, .18):
        for y in (-.18, .18):
            s.box(body, (x, y, .21), (.045, .045, .42), 'oak')


def shelf(s, name, center, w, d, h):
    body = s.item(name, center, (w, d))
    s.box(body, (0, d / 2 - .02, h / 2), (w, .04, h), 'oak')
    for x in (-w / 2 + .025, w / 2 - .025):
        s.box(body, (x, 0, h / 2), (.05, d, h), 'lightwood')
    for z in (.05, .45, .9, 1.35, h - .025):
        s.box(body, (0, 0, z), (w, d, .05), 'lightwood')
    for level in (.48, .93, 1.38):
        for i, color in enumerate(('blue', 'clay', 'sage', 'yellow')):
            s.box(body, (-w / 2 + .13 + i * .10, -.02, level + .12),
                  (.07, d * .65, .24), color)


def plant(s, name, center):
    body = s.item(name, center, (.50, .50))
    s.geom(body, 'cylinder', (0, 0, .19), (.16, .16, .19), 'clay')
    s.box(body, (0, 0, .68), (.035, .035, .8), 'oak')
    for i in range(6):
        angle = i * math.pi / 3
        s.geom(body, 'sphere', (.10 * math.cos(angle), .10 * math.sin(angle), .66 + i * .08),
               (.14, .14, .18), 'green')


def furniture(s):
    fridge = s.item('Kuehlschrank', (.5, .53), (.70, .76))
    s.box(fridge, (0, 0, .95), (.7, .72, 1.9), 'white')
    s.box(fridge, (0, .368, .58), (.65, .024, 1.05), 'metal')
    s.box(fridge, (0, .368, 1.5), (.65, .024, .65), 'white')
    s.box(fridge, (.22, .375, 1.02), (.035, .01, .30), 'dark')
    kitchen = s.item('Kuechenzeile', (3.43, .475), (1.94, .65))
    s.box(kitchen, (0, 0, .44), (1.9, .62, .88), 'sage')
    s.box(kitchen, (0, 0, .90), (1.94, .65, .04), 'white')
    for x in (-.65, 0, .65):
        s.box(kitchen, (x, .314, .45), (.60, .012, .75), 'sage')
        s.box(kitchen, (x, .32, .75), (.20, .01, .025), 'metal')
    s.box(kitchen, (-.4, 0, .925), (.58, .45, .01), 'metal')
    s.box(kitchen, (-.4, 0, .932), (.45, .32, .008), 'dark')
    s.box(kitchen, (-.4, -.23, 1.04), (.035, .035, .25), 'metal')
    s.box(kitchen, (-.4, -.15, 1.15), (.035, .19, .035), 'metal')
    s.box(kitchen, (.55, 0, .93), (.56, .49, .02), 'dark')
    for x in (.42, .70):
        for y in (-.12, .12):
            s.geom(kitchen, 'cylinder', (x, y, .945), (.09, .09, .006), 'metal')
    table(s, 'Esstisch', (1.7, 2.65), 1.25, .85, .76)
    chair(s, 'Essstuhl_Sued', (1.7, 1.9))
    chair(s, 'Essstuhl_Nord', (1.7, 3.4), 180)
    shelf(s, 'Regal_Kueche', (.55, 4.15), .8, .4, 1.8)

    sofa = s.item('Sofa', (.68, 7.2), (1.0, 2.25))
    s.box(sofa, (0, 0, .24), (.94, 2.2, .32), 'dark')
    s.box(sofa, (-.4, 0, .65), (.2, 2.25, .78), 'blue')
    for y in (-1.02, 1.02):
        s.box(sofa, (0, y, .54), (1., .21, .55), 'blue')
    for y in (-.65, 0, .65):
        s.box(sofa, (.08, y, .49), (.78, .61, .22), 'blue')
    s.geom(sofa, 'sphere', (-.15, .7, .70), (.16, .24, .21), 'yellow')
    table(s, 'Couchtisch', (2.15, 7.05), .8, .85, .44)
    tv = s.item('Fernseher', (2.35, 8.65), (1.65, .45))
    s.box(tv, (0, 0, .28), (1.65, .45, .50), 'oak')
    s.box(tv, (0, 0, .62), (.35, .25, .18), 'dark')
    s.box(tv, (0, .03, 1.08), (1.3, .09, .74), 'dark')
    s.box(tv, (0, -.018, 1.08), (1.20, .008, .64), 'screen')
    plant(s, 'Pflanze_Wohnzimmer', (4.05, 8.6))

    bed = s.item('Bett', (7.7, 1.65), (2.25, 1.9))
    s.box(bed, (0, 0, .23), (2.2, 1.85, .36), 'oak')
    s.box(bed, (0, 0, .49), (2.16, 1.8, .23), 'white')
    s.box(bed, (1.075, 0, .62), (.1, 1.9, 1.15), 'lightwood')
    s.box(bed, (-.3, 0, .62), (1.5, 1.82, .06), 'sage')
    for y in (-.46, .46):
        s.geom(bed, 'sphere', (.72, y, .65), (.29, .36, .10), 'linen')
    wardrobe = s.item('Kleiderschrank', (5.5, .5), (1.65, .7))
    s.box(wardrobe, (0, 0, 1.05), (1.65, .68, 2.1), 'lightwood')
    for x in (-.42, .42):
        s.box(wardrobe, (x, .343, 1.08), (.79, .014, 2.0), 'linen')
        s.box(wardrobe, (x / 4, .348, 1.05), (.025, .004, .3), 'metal')
    table(s, 'Nachttisch', (8.5, 3.02), .65, .55, .55)

    desk = table(s, 'Schreibtisch', (7.95, 8.5), 1.8, .75, .76)
    s.box(desk, (0, .18, .83), (.35, .20, .14), 'dark')
    s.box(desk, (0, .19, 1.10), (.65, .06, .42), 'dark')
    s.box(desk, (0, .155, 1.10), (.59, .005, .35), 'screen')
    s.box(desk, (0, -.16, .81), (.48, .18, .025), 'dark')
    shelf(s, 'Regal', (5.65, 8.65), 1.7, .45, 1.9)
    plant(s, 'Pflanze_Buero', (8.6, 4.95))


def person(s, name, center, color, yaw=0, seated=False):
    body = s.item(name, center, (.64, .82 if seated else .46), yaw)
    if seated:
        chair_parts(s, body)
    hip = .61 if seated else .95
    for x in (-.11, .11):
        if seated:
            s.box(body, (x, .12, .55), (.15, .44, .16), 'dark')
            s.box(body, (x, .30, .31), (.13, .13, .46), 'dark')
        else:
            s.box(body, (x, 0, .49), (.15, .17, .84), 'dark')
        s.box(body, (x, .31 if seated else .05, .06), (.17, .19 if seated else .3, .12), 'dark')
    s.geom(body, 'sphere', (0, 0, hip + .24), (.23, .15, .32), color)
    for x in (-.265, .265):
        s.geom(body, 'sphere', (x, 0, hip + .17), (.05, .08, .26), color)
        s.geom(body, 'sphere', (x, .02, hip - .06), (.05, .06, .08), 'skin')
    s.geom(body, 'cylinder', (0, 0, hip + .56), (.065, .065, .08), 'skin')
    s.geom(body, 'sphere', (0, 0, hip + .73), (.115, .11, .15), 'skin')
    s.geom(body, 'sphere', (0, -.015, hip + .81), (.118, .10, .085), 'hair')
    for x in (-.04, .04):
        s.geom(body, 'sphere', (x, .102, hip + .75), (.013, .009, .012), 'dark')


def bottle(s, name, support, position, color, diameter, height, approach):
    """Upright capped bottle; local origin is the centre of its bottom face."""
    body = s.prop(name, 'bottle', support, position)
    r, cap_height = diameter / 2, .016
    shell_height = height - cap_height
    s.geom(body, 'bottle', (0, 0, 0), (.98 * r, .98 * r, shell_height), color)
    # Label sits on the full-radius cylindrical section; it never bridges the shoulder.
    s.geom(body, 'cylinder', (0, 0, shell_height * .40),
           (r, r, shell_height * .17), 'linen')
    s.geom(body, 'cylinder', (0, 0, height - cap_height / 2),
           (.48 * r, .48 * r, cap_height / 2), 'white')
    # Stable, invisible reference for future perception/IK experiments. An arm's
    # reach, gripper aperture, approach orientation and collision-free motion are
    # deliberately not guessed here.
    site = 'arena_' + name + '_grasp'
    grip_z = round(shell_height * .4, 6)
    ET.SubElement(body, 'site', name=site, pos=numbers((0, 0, grip_z)),
                  size='.003', rgba='0 0 0 0', group='5')
    s.props[name].update(dimensions_m=[diameter, diameter, height],
                         approach_place=approach,
                         grasp_reference=dict(site=site, position_local=[0, 0, grip_z],
                                              diameter_m=diameter, status='unvalidated'))


def mug(s, name, support, position, color):
    body = s.prop(name, 'mug', support, position)
    s.geom(body, 'cup', (0, 0, 0), (.043, .043, .095), color)
    for z in (.025, .078):
        s.box(body, (.057, 0, z), (.046, .014, .014), color)
    s.box(body, (.077, 0, .0515), (.014, .014, .067), color)


def book(s, name, support, position, color):
    body = s.prop(name, 'book', support, position)
    s.box(body, (0, 0, .017), (.17, .23, .028), 'linen')
    for z in (.0015, .0325):
        s.box(body, (0, 0, z), (.18, .24, .003), color)
    s.box(body, (-.088, 0, .017), (.004, .24, .034), color)


def tabletop_props(s):
    # Bottles are near unobstructed table edges at different heights. These
    # navigation approach places do not certify arm reach or gripper suitability.
    bottle(s, 'Flasche_Esstisch', 'Esstisch', (1.30, 2.65, .76),
           'blue', .070, .26, 'Esstisch')
    bottle(s, 'Flasche_Couchtisch', 'Couchtisch', (2.15, 6.80, .44),
           'green', .065, .24, 'Couchtisch')
    bottle(s, 'Flasche_Schreibtisch', 'Schreibtisch', (7.25, 8.29, .76),
           'clay', .075, .28, 'Schreibtisch')
    bottle(s, 'Flasche_Nachttisch', 'Nachttisch', (8.38, 3.04, .55),
           'blue', .060, .22, 'Nachttisch')
    mug(s, 'Tasse_Esstisch', 'Esstisch', (2.04, 2.45, .76), 'clay')
    mug(s, 'Tasse_Schreibtisch', 'Schreibtisch', (8.56, 8.35, .76), 'white')
    book(s, 'Buch_Couchtisch', 'Couchtisch', (2.36, 7.23, .44), 'clay')
    book(s, 'Buch_Nachttisch', 'Nachttisch', (8.65, 3.02, .55), 'blue')
    remote = s.prop('Fernbedienung', 'remote', 'Couchtisch', (1.96, 7.25, .44))
    s.box(remote, (0, 0, .012), (.045, .16, .024), 'dark')
    for y in (-.045, -.015, .015, .045):
        s.box(remote, (0, y, .025), (.022, .012, .003), 'metal')
    bowl = s.prop('Obstschale', 'fruit_bowl', 'Esstisch', (1.85, 2.87, .76))
    s.geom(bowl, 'cup', (0, 0, 0), (.13, .13, .065), 'white')
    for i, color in enumerate(('green', 'clay', 'yellow')):
        angle = i * 2 * math.pi / 3
        x, y = .046 * math.cos(angle), .046 * math.sin(angle)
        # Fruit bottom lies on the bowl's inner base (13% of bowl height).
        z = .065 * .13 + .04
        s.geom(bowl, 'sphere', (x, y, z), (.04, .04, .04), color)
        s.box(bowl, (x, y, z + .042), (.005, .005, .012), 'oak')


PLACES = {
    'Eingang': (1.6, .65), 'Sofa': (1.7, 6.1), 'Couchtisch': (2.15, 6.10),
    'Fernseher': (2.35, 8.0), 'Esstisch': (.55, 2.65), 'Kuehlschrank': (.5, 1.45),
    'Spuele': (3.03, 1.35), 'Bett': (6.0, 1.8), 'Kleiderschrank': (5.5, 1.4),
    'Schreibtisch': (7.05, 7.6), 'Regal': (5.65, 7.85), 'Nachttisch': (8.45, 3.85),
    'Mitte': START, 'Person_Kueche': (2.85, 2.1),
    'Person_Wohnzimmer': (3.8, 6.85), 'Person_Buero': (8.0, 6.55),
}


def build():
    """Return deterministic YAML data, MJCF include and original OBJ texts."""
    s = Scene()
    architecture(s)
    furniture(s)
    tabletop_props(s)
    person(s, 'Person_Kueche', (3.65, 2.1), 'clay', yaw=90)
    person(s, 'Person_Wohnzimmer', (3.8, 7.75), 'sage', yaw=180)
    person(s, 'Person_Buero', (8.0, 7.5), 'blue', yaw=180, seated=True)
    objects = {name: dict(type='place', frame='map', position=list(pos))
               for name, pos in PLACES.items()}
    objects['Start'] = dict(type='sim_start', frame='map', position=list(START))
    boundary = dict(name='Arena', type='boundary', frame='map', color='orange',
                    points=rectangle((-.5, -.5, 9.5, 9.5)))
    doc = {'map': dict(resolution=RESOLUTION, origin=[-.5, -.5], width_px=200,
                       height_px=200, width_m=10., height_m=10.,
                       source='pkg_sim/tools/build_arena.py (original procedural arena)'),
           'objects': objects, 'polygons': s.polygons + [boundary],
           'scene_objects': s.props}
    ET.indent(s.root, space='  ')
    xml = '<!-- Generated by build_arena.py; original geometry, metres, Z up. -->\n'
    xml += ET.tostring(s.root, encoding='unicode') + '\n'
    return doc, xml, original_meshes()


def write(output_dir=MAPS):
    output_dir = Path(output_dir)
    doc, xml, meshes = build()
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / 'arena_meshes').mkdir(exist_ok=True)
    for name, content in meshes.items():
        (output_dir / 'arena_meshes' / name).write_text(content, encoding='utf-8')
    (output_dir / 'Arena.yaml').write_text(
        '# Generated by build_arena.py; edit the generator, not this file.\n'
        + yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding='utf-8')
    (output_dir / 'Arena_visuals.xml').write_text(xml, encoding='utf-8')
    return doc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=MAPS)
    args = parser.parse_args()
    doc = write(args.output_dir)
    print(f'{args.output_dir}/Arena.yaml: {len(doc["polygons"])} polygons, '
          f'{len(doc["objects"]) - 1} destinations; visuals and original meshes written.')


if __name__ == '__main__':
    main()
