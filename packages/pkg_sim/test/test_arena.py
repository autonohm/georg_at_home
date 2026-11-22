"""Acceptance checks on the delivered Arena files, without ROS or Docker.

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest packages/pkg_sim/test/test_arena.py

MuJoCo is required, not silently skipped. The dedicated version test enforces
the requested 3.16 runtime; use the project's macOS environment or sim image.
"""

from collections import deque
import importlib.util
import itertools
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

import mujoco
import numpy as np
import pytest
import yaml

SIM = Path(__file__).resolve().parents[1]
MAPS = SIM.parent / 'pkg_slam' / 'maps'
sys.path.insert(0, str(SIM / 'georg_sim'))
from georg_sim.mjcf import build_mjcf  # noqa: E402
from georg_sim.world import World  # noqa: E402


@pytest.fixture(scope='module')
def arena():
    return yaml.safe_load((MAPS / 'Arena.yaml').read_text())


def polygon_metrics(points, polygon):
    """Independent vectorized ray crossing and exact distance to polygon edges."""
    points = np.asarray(points)
    x, y = points[..., 0], points[..., 1]
    inside = np.zeros(x.shape, dtype=bool)
    distance = np.full(x.shape, np.inf)
    poly = np.asarray(polygon, dtype=float)
    for a, b in zip(poly, np.roll(poly, -1, axis=0)):
        v = b - a
        t = np.clip(((x - a[0]) * v[0] + (y - a[1]) * v[1]) / np.dot(v, v), 0, 1)
        distance = np.minimum(distance, np.hypot(x - a[0] - t * v[0], y - a[1] - t * v[1]))
        if v[1] != 0:
            inside ^= ((a[1] > y) != (b[1] > y)) & (x < a[0] + (y - a[1]) * v[0] / v[1])
    return inside, distance


def clearance(points, arena):
    result = np.full(np.asarray(points).shape[:-1], np.inf)
    for poly in arena['polygons']:
        inside, distance = polygon_metrics(points, poly['points'])
        invalid = ~inside if poly['type'] == 'boundary' else inside
        result = np.minimum(result, np.where(invalid, -distance, distance))
    return result


def test_schema_and_required_places(arena):
    required = {'Eingang', 'Sofa', 'Couchtisch', 'Fernseher', 'Esstisch', 'Kuehlschrank',
                'Spuele', 'Bett', 'Kleiderschrank', 'Schreibtisch', 'Regal', 'Mitte'}
    objects = arena['objects']
    assert required <= objects.keys()
    assert [n for n, o in objects.items() if o['type'] == 'sim_start'] == ['Start']
    assert all(o['type'] == 'place' for n, o in objects.items() if n != 'Start')
    assert all(o['frame'] == 'map' and len(o['position']) == 2 for o in objects.values())
    people = {p['name'] for p in arena['polygons'] if p['name'].startswith('Person_')}
    assert 2 <= len(people) <= 4
    assert people <= objects.keys()
    assert sum(p['type'] == 'boundary' for p in arena['polygons']) == 1
    m = arena['map']
    assert m['resolution'] == .05
    for axis in ('width', 'height'):
        assert m[axis + '_px'] * m['resolution'] == pytest.approx(m[axis + '_m'])
    assert len({p['name'] for p in arena['polygons']}) == len(arena['polygons'])
    origin = np.asarray(m['origin'])
    upper = origin + [m['width_m'], m['height_m']]
    for poly in arena['polygons']:
        pts = np.asarray(poly['points'])
        assert poly['type'] in ('obstacle', 'boundary')
        assert np.isfinite(pts).all() and len(pts) >= 3
        assert (pts >= origin).all() and (pts <= upper).all()


def test_every_destination_and_start_has_40cm_clearance(arena):
    for name, obj in arena['objects'].items():
        actual = float(clearance(np.asarray(obj['position']), arena))
        assert actual >= .4 - 1e-9, f'{name}: only {actual:.3f} m clearance'


@pytest.mark.parametrize('radius', [.25, .35])
def test_every_destination_reachable_on_5cm_grid(arena, radius):
    # Cell centres; a half-cell diagonal keeps the ENTIRE visited cell clear,
    # so the four-connected path cannot cut a corner or graze an obstacle.
    m = arena['map']
    cell = m['resolution']
    origin = np.asarray(m['origin'])
    yy, xx = np.mgrid[:m['height_px'], :m['width_px']]
    points = origin + (np.stack((xx, yy), axis=-1) + .5) * cell
    free = clearance(points, arena) > radius + cell / np.sqrt(2)
    # No routing around exterior walls: every room must connect inside 9 x 9 m.
    free &= (points[..., 0] > 0) & (points[..., 0] < 9)
    free &= (points[..., 1] > 0) & (points[..., 1] < 9)

    def index(position):
        x, y = np.floor((np.asarray(position) - origin) / cell).astype(int)
        return int(y), int(x)

    start = index(arena['objects']['Start']['position'])
    assert free[start], 'Start cell is blocked'
    seen = {start}
    pending = deque([start])
    while pending:
        y, x = pending.popleft()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            q = y + dy, x + dx
            if (0 <= q[0] < free.shape[0] and 0 <= q[1] < free.shape[1]
                    and free[q] and q not in seen):
                seen.add(q)
                pending.append(q)
    for name, obj in arena['objects'].items():
        assert index(obj['position']) in seen, f'{name} unreachable at radius {radius}'


@pytest.fixture(scope='module')
def model():
    path = MAPS / 'Arena_visuals.xml'
    # File-based includes exercise the relative asset paths used at deployment.
    return mujoco.MjModel.from_xml_string(
        f'<mujoco><include file="{path}"/></mujoco>')


def test_mujoco_316_loads(model):
    assert mujoco.__version__.split('.')[:2] == ['3', '16'], (
        f'Acceptance requires MuJoCo 3.16, found {mujoco.__version__}')
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    assert model.ngeom > 100
    assert np.isfinite(data.geom_xpos).all()
    assert (model.geom_contype == 0).all()
    assert (model.geom_conaffinity == 0).all()


def test_visuals_load_with_existing_simulator(arena):
    world = World.from_yaml(str(MAPS / 'Arena.yaml'))
    start = (*arena['objects']['Start']['position'], 0)
    root = ET.fromstring(build_mjcf(world, start, .35))
    include = ET.parse(MAPS / 'Arena_visuals.xml').getroot()
    root.find('compiler').set('meshdir', str(MAPS))
    root.append(include.find('asset'))
    root.find('worldbody').extend(include.find('worldbody'))
    compiled = mujoco.MjModel.from_xml_string(ET.tostring(root, encoding='unicode'))
    data = mujoco.MjData(compiled)
    mujoco.mj_resetDataKeyframe(compiled, data, 0)
    mujoco.mj_forward(compiled, data)
    assert data.qpos == pytest.approx(start)
    for _ in range(50):
        mujoco.mj_step(compiled, data)
    assert data.ncon == 0, 'Arena start intersects the physical world'


def test_triangle_budget_counts_every_instance(model):
    # Count drawn triangles, including repeated mesh instances, not just assets.
    triangles = 0
    for i, kind in enumerate(model.geom_type):
        if kind == mujoco.mjtGeom.mjGEOM_BOX:
            triangles += 12
        else:
            assert kind == mujoco.mjtGeom.mjGEOM_MESH, 'Unaccounted primitive in budget'
            triangles += int(model.mesh_facenum[model.geom_dataid[i]])
    assert 0 < triangles <= 300_000, triangles


def test_mesh_assets_are_local_closed_original_objs():
    include = ET.parse(MAPS / 'Arena_visuals.xml').getroot()
    for mesh in include.findall('asset/mesh'):
        path = Path(mesh.attrib['file'])
        assert not path.is_absolute() and '..' not in path.parts
        assert path.parts[0] == 'arena_meshes' and path.suffix == '.obj'
    for path in (MAPS / 'arena_meshes').glob('*.obj'):
        lines = path.read_text().splitlines()
        assert lines[0].startswith('# Original procedural geometry:')
        verts = np.asarray([[float(v) for v in line.split()[1:]] for line in lines if line.startswith('v ')])
        faces = [[int(v.split('/')[0]) - 1 for v in line.split()[1:]] for line in lines if line.startswith('f ')]
        edges = {}
        volume = 0
        for face in faces:
            assert len(face) == 3 and len(set(face)) == 3
            a, b, c = verts[face]
            assert np.linalg.norm(np.cross(b - a, c - a)) > 1e-9
            volume += np.dot(a, np.cross(b, c)) / 6
            for edge in zip(face, face[1:] + face[:1]):
                edges[edge] = edges.get(edge, 0) + 1
        assert volume > 0
        assert all(count == 1 and edges.get((b, a)) == 1 for (a, b), count in edges.items())


def geom_vertices(model, data, i):
    """World-space rendered vertices, including MuJoCo's mesh recentering."""
    if model.geom_type[i] == mujoco.mjtGeom.mjGEOM_BOX:
        vertices = np.asarray(list(itertools.product((-1, 1), repeat=3))) * model.geom_size[i]
    else:
        mid = model.geom_dataid[i]
        address, count = model.mesh_vertadr[mid], model.mesh_vertnum[mid]
        vertices = model.mesh_vert[address:address + count]
    return vertices @ data.geom_xmat[i].reshape(3, 3).T + data.geom_xpos[i]


def body_bounds(model, data, body_id):
    indices = np.flatnonzero(model.geom_bodyid == body_id)
    points = np.concatenate([geom_vertices(model, data, i) for i in indices])
    return np.stack((points.min(axis=0), points.max(axis=0)))


def test_tabletop_props_have_stable_poses_and_rest_on_supports(arena, model):
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    props = arena['scene_objects']
    assert {'bottle', 'mug', 'book', 'remote', 'fruit_bowl'} <= {p['category'] for p in props.values()}
    assert not (props.keys() & arena['objects'].keys()), '3D props must not become 2D navigation goals'
    bounds = {}
    for name, prop in props.items():
        bid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, prop['body'])
        assert bid > 0, name
        assert prop['frame'] == 'map' and prop['simulation'] == 'static_visual'
        assert model.body_jntnum[bid] == 0
        assert data.xpos[bid] == pytest.approx(prop['position'])
        lo, hi = body_bounds(model, data, bid)
        bounds[name] = (lo, hi)
        base_z = prop['position'][2]
        assert lo[2] == pytest.approx(base_z, abs=1e-6), f'{name} floating or sunken'
        support = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, 'arena_' + prop['support'])
        assert support > 0
        supported = False
        for i in np.flatnonzero(model.geom_bodyid == support):
            vertices = geom_vertices(model, data, i)
            a, b = vertices.min(axis=0), vertices.max(axis=0)
            overlap = np.minimum(hi, b) - np.maximum(lo, a)
            assert not (overlap > 1e-5).all(), f'{name} intersects support equipment'
            supported |= (model.geom_type[i] == mujoco.mjtGeom.mjGEOM_BOX
                          and abs(b[2] - base_z) < 1e-6
                          and (lo[:2] >= a[:2] + .01).all()
                          and (hi[:2] <= b[:2] - .01).all())
        assert supported, f'{name} not fully on a tabletop with a 1cm margin'
    for first, second in itertools.combinations(bounds, 2):
        a, b = bounds[first], bounds[second]
        overlap = np.minimum(a[1], b[1]) - np.maximum(a[0], b[0])
        assert not (overlap > 1e-5).all(), f'{first} intersects {second}'


def test_bottle_grasp_references_match_geometry_and_leave_room(arena, model):
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    props = arena['scene_objects']
    bottles = {n: p for n, p in props.items() if p['category'] == 'bottle'}
    assert len(bottles) == 4
    for name, prop in bottles.items():
        bid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, prop['body'])
        lo, hi = body_bounds(model, data, bid)
        assert hi - lo == pytest.approx(prop['dimensions_m'], abs=1e-6)
        diameter, _, height = prop['dimensions_m']
        assert .05 <= diameter <= .08 and .20 <= height <= .30
        reference = prop['grasp_reference']
        sid = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_SITE, reference['site'])
        assert sid >= 0 and model.site_bodyid[sid] == bid
        assert model.site_rgba[sid, 3] == 0, 'Reference marker must not pollute camera images'
        assert reference['status'] == 'unvalidated'
        assert model.site_pos[sid] == pytest.approx(reference['position_local'])
        assert data.site_xpos[sid] == pytest.approx(
            np.asarray(prop['position']) + reference['position_local'])
        assert reference['diameter_m'] == pytest.approx(diameter)
        assert .2 * height < reference['position_local'][2] < .6 * height
        place = arena['objects'][prop['approach_place']]
        assert place['type'] == 'place'
        # This is an approach distance, not an arm reachability certificate.
        assert np.linalg.norm(np.asarray(place['position']) - prop['position'][:2]) < 1.
        for other_name, other in props.items():
            if other_name == name:
                continue
            other_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, other['body'])
            other_lo, other_hi = body_bounds(model, data, other_id)
            gap = np.maximum(np.maximum(other_lo[:2] - hi[:2], lo[:2] - other_hi[:2]), 0)
            assert np.linalg.norm(gap) >= .12, f'{name}: nearby clutter obstructs future approach'


def test_map_covers_all_visible_obstacles_below_one_metre(arena, model):
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    polygons = [p['points'] for p in arena['polygons'] if p['type'] == 'obstacle']
    for i in range(model.ngeom):
        name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_GEOM, i)
        if name.startswith('arena_floor_'):
            continue
        world = geom_vertices(model, data, i)
        if world[:, 2].min() >= 1:
            continue
        covered = np.zeros(len(world), dtype=bool)
        for poly in polygons:
            inside, dist = polygon_metrics(world[:, :2], poly)
            covered |= inside | (dist < 1e-5)
        assert covered.all(), f'{name}: visible geometry missing from obstacle map'


def test_rooms_have_full_height_walls_and_clear_doorways(arena, model):
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    for poly in arena['polygons']:
        if poly['name'].startswith('Wand_'):
            p = np.mean(poly['points'], axis=0)
            matching = np.linalg.norm(data.geom_xpos[:, :2] - p, axis=1) < 1e-5
            assert any(abs(model.geom_size[i, 2] * 2 - 2.4) < 1e-6
                       for i in np.flatnonzero(matching))
    # A 1.2 m clear corridor through each opening covers base radius + inflation.
    for center, along in [((1.6, 0), (0, 1)), ((3.2, 4.5), (0, 1)),
                          ((5.8, 4.5), (0, 1)), ((4.5, 3.5), (1, 0)),
                          ((4.5, 5.8), (1, 0))]:
        samples = np.asarray(center) + np.linspace(-.15, .15, 7)[:, None] * along
        # Ignore map boundary only at the entrance, where no robot target is placed.
        obstacles_only = {'polygons': [p for p in arena['polygons'] if p['type'] == 'obstacle']}
        assert (clearance(samples, obstacles_only) >= .60).all(), center


def test_generation_is_reproducible_and_self_contained(tmp_path):
    spec = importlib.util.spec_from_file_location('build_arena', SIM / 'tools' / 'build_arena.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.write(tmp_path)
    generated = sorted(p.relative_to(tmp_path) for p in tmp_path.rglob('*') if p.is_file())
    assert set(generated) == {Path('Arena.yaml'), Path('Arena_visuals.xml'),
                              Path('arena_meshes/sphere.obj'), Path('arena_meshes/cylinder.obj'),
                              Path('arena_meshes/bottle.obj'), Path('arena_meshes/cup.obj')}
    for path in generated:
        assert (tmp_path / path).read_bytes() == (MAPS / path).read_bytes(), str(path)
