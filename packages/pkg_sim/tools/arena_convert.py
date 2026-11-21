"""Convert the RoboCup@Home arena (USD) into the simulation world of Georg.

    docker run --rm -v <repo>/packages:/packages sim bash -c \
      "pip install -q --break-system-packages usd-core && \
       python3 /packages/pkg_sim/tools/arena_convert.py \
         /packages/pkg_sim/assets/arena/Competition_Arena_AtHome.usdc \
         /packages/pkg_sim/assets/arena/generated /packages/pkg_slam/maps/Arena_AtHome.yaml"

Outputs
  <out>/meshes/<object>.obj   simplified visual meshes in world coordinates (camera image)
  <out>/arena_visuals.xml     MJCF snippet: <asset> meshes/materials + <geom>s (no collision)
  <map>                       map YAML like pkg_slam/maps/Nav_Test.yaml: footprints of walls and
                              furniture as obstacle polygons (physics, lidar, navigation) and
                              named places (navigation targets) in front of the furniture

Only geometry and colours are taken; the USD and its meshes stay out of git (pkg_sim/assets).
"""
import argparse
import math
import os
import re

import numpy as np
import yaml

try:  # the geometry helpers below are also used by build_world.py, without USD
    from pxr import Gf, Usd, UsdGeom, UsdShade
except ImportError:
    Gf = Usd = UsdGeom = UsdShade = None

# GroundPlane: 50 m helper plane 2 m below the arena (Isaac Sim), not part of the room
SKIP_TOP = {'_materials', 'Light', 'Render', 'Graph', 'PhysicsScene', 'kaya', 'GroundPlane'}
FLOOR_NAMES = {'ArenaFloor', 'Plane'}   # visual only, no obstacle
MAP_MARGIN_M = 0.3
MAX_TRIS_PER_OBJECT = 90000          # keeps the MuJoCo scene light for the camera
OBSTACLE_MAX_Z = 1.0                 # only parts below this height block Georg's base/lidar
OBSTACLE_MIN_HEIGHT = 0.05           # ignore flat things (rugs)

# navigation targets: object name pattern -> place name (stand in front of it)
PLACES = [
    (r'^Peru_3_Seater_Sofa$', 'Sofa'),
    (r'^Living_Room_Table$', 'Wohnzimmertisch'),
    (r'^Modern_King_Bed$', 'Bett'),
    (r'^Refrigerator$', 'Kuehlschrank'),
    (r'^Sink$', 'Spuele'),
    (r'^Ikea_Desk_With_two_Drawer$', 'Schreibtisch'),
    (r'^Dishwasher_01$', 'Spuelmaschine'),
    (r'^Washing_machine$', 'Waschmaschine'),
    (r'^Modern_Wardrobe$', 'Kleiderschrank'),
    (r'^Table$', 'Esstisch'),
    (r'^Door_Group_001$', 'Tuer1'),
    (r'^Door_Group_002$', 'Tuer2'),
]


def _color(prim):
    """Diffuse colour of the bound material (UsdPreviewSurface) or displayColor, else grey."""
    gprim = UsdGeom.Gprim(prim)
    dc = gprim.GetDisplayColorAttr().Get() if gprim else None
    material, _ = UsdShade.MaterialBindingAPI(prim).ComputeBoundMaterial()
    if material:
        for shader_prim in Usd.PrimRange(material.GetPrim()):
            shader = UsdShade.Shader(shader_prim)
            if not shader:
                continue
            inp = shader.GetInput('diffuseColor') or shader.GetInput('diffuse_color_constant')
            if inp and inp.Get() is not None:
                c = inp.Get()
                return [float(c[0]), float(c[1]), float(c[2])]
    if dc:
        return [float(v) for v in dc[0]]
    return [0.7, 0.7, 0.7]


def _triangles(mesh_prim, cache):
    """World-space vertices and triangle indices of one USD mesh."""
    mesh = UsdGeom.Mesh(mesh_prim)
    points = mesh.GetPointsAttr().Get()
    counts = mesh.GetFaceVertexCountsAttr().Get()
    indices = mesh.GetFaceVertexIndicesAttr().Get()
    if not points or not counts:
        return None, None
    xf = cache.GetLocalToWorldTransform(mesh_prim)
    pts = np.array([xf.Transform(Gf.Vec3d(*p)) for p in points], dtype=np.float64)
    tris, i = [], 0
    for c in counts:
        face = indices[i:i + c]
        for k in range(1, c - 1):        # fan triangulation
            tris.append((face[0], face[k], face[k + 1]))
        i += c
    return pts, np.array(tris, dtype=np.int64)


def _simplify(verts, tris, max_tris):
    """Vertex clustering: merge vertices on a grid until the triangle count fits."""
    if len(tris) <= max_tris:
        return verts, tris
    size = max(np.ptp(verts, axis=0).max(), 1e-3)
    cell = size / 400.0
    while True:
        keys = np.floor(verts / cell).astype(np.int64)
        _, inverse = np.unique(keys, axis=0, return_inverse=True)
        inverse = inverse.reshape(-1)
        t = inverse[tris]
        t = t[(t[:, 0] != t[:, 1]) & (t[:, 1] != t[:, 2]) & (t[:, 0] != t[:, 2])]
        t = np.unique(np.sort(t, axis=1), axis=0)
        if len(t) <= max_tris or cell > size / 10:
            counts = np.bincount(inverse)
            sums = np.zeros((counts.size, 3))
            np.add.at(sums, inverse, verts)
            return sums / counts[:, None], t
        cell *= 1.5


def _write_obj(path, verts, tris):
    with open(path, 'w', encoding='utf-8') as f:
        for v in verts:
            f.write(f'v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}\n')
        for a, b, c in tris + 1:
            f.write(f'f {a} {b} {c}\n')


def _safe(name):
    return re.sub(r'[^A-Za-z0-9_]', '_', name)


def collect(stage):
    """Objects under /root: name -> (vertices, triangles, rgb)."""
    cache = UsdGeom.XformCache(Usd.TimeCode.Default())
    root = stage.GetPrimAtPath('/root')
    objects = {}
    for top in root.GetChildren():
        if top.GetName() in SKIP_TOP:
            continue
        parts, colors = [], []
        prims = [top] + list(Usd.PrimRange(top))
        for prim in prims:
            if not prim.IsA(UsdGeom.Mesh):
                continue
            img = UsdGeom.Imageable(prim)
            if img and img.ComputeVisibility() == UsdGeom.Tokens.invisible:
                continue
            verts, tris = _triangles(prim, cache)
            if verts is None or len(tris) == 0:
                continue
            parts.append((verts, tris))
            colors.append((_color(prim), len(tris)))
        if not parts:
            continue
        offset, vs, ts = 0, [], []
        for verts, tris in parts:
            vs.append(verts)
            ts.append(tris + offset)
            offset += len(verts)
        weights = np.array([n for _, n in colors], dtype=float)
        rgb = (np.array([c for c, _ in colors]) * weights[:, None]).sum(0) / weights.sum()
        objects[top.GetName()] = (np.vstack(vs), np.vstack(ts), rgb.tolist())
    return objects


def _hull(points):
    """Convex hull (monotone chain), counter-clockwise."""
    pts = sorted(set(map(tuple, np.round(points, 3))))
    if len(pts) < 3:
        return [list(p) for p in pts]

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower, upper = [], []
    for pt in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], pt) <= 0:
            lower.pop()
        lower.append(pt)
    for pt in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], pt) <= 0:
            upper.pop()
        upper.append(pt)
    return [list(p) for p in lower[:-1] + upper[:-1]]


def _edge_samples(verts, tris, step=0.025):
    """Points along all triangle edges (dense enough to connect the corners of a box)."""
    a = verts[np.concatenate([tris[:, 0], tris[:, 1], tris[:, 2]])]
    b = verts[np.concatenate([tris[:, 1], tris[:, 2], tris[:, 0]])]
    n = np.maximum(1, np.ceil(np.linalg.norm(b - a, axis=1) / step).astype(int))
    out = [verts]
    for k in np.unique(n):
        sel = n == k
        t = np.linspace(0.0, 1.0, k + 1)[None, :, None]
        out.append((a[sel][:, None, :] + (b[sel] - a[sel])[:, None, :] * t).reshape(-1, 3))
    return np.vstack(out)


def footprints(verts, tris, cell=0.05):
    """Convex hulls (XY) of the separate parts that block a mobile base (below 1 m).

    Hulls instead of axis-aligned boxes (turned chairs, open doors), and one hull per connected
    part: the two posts of a door frame must not close the doorway between them.
    """
    if np.ptp(verts[:, 2]) < OBSTACLE_MIN_HEIGHT:
        return []
    pts = _edge_samples(verts, tris)
    low = pts[pts[:, 2] < OBSTACLE_MAX_Z][:, :2]
    if len(low) < 3:
        return []
    keys = np.floor(low / cell).astype(np.int64)
    cells = {tuple(k) for k in keys}
    label, n = {}, 0
    for c in cells:
        if c in label:
            continue
        stack = [c]
        label[c] = n
        while stack:
            i, j = stack.pop()
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    q = (i + di, j + dj)
                    if q in cells and q not in label:
                        label[q] = n
                        stack.append(q)
        n += 1
    ids = np.array([label[tuple(k)] for k in keys])
    hulls = []
    for part in range(n):
        pts = low[ids == part]
        if len(pts) < 3:
            continue
        hull = _hull(pts)
        if len(hull) >= 3:
            hulls.append(hull)
    return hulls


def _inside(x, y, poly):
    inside = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside = not inside
    return inside


def _dist(x, y, poly):
    best = math.inf
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        dx, dy = x2 - x1, y2 - y1
        t = 0.0 if dx == dy == 0 else max(0.0, min(1.0, ((x - x1) * dx + (y - y1) * dy) /
                                                    (dx * dx + dy * dy)))
        best = min(best, math.hypot(x - x1 - t * dx, y - y1 - t * dy))
    return best


def is_free(x, y, polygons, radius):
    """No obstacle polygon within radius of (x, y)."""
    return all(not _inside(x, y, p) and _dist(x, y, p) > radius for p in polygons)


def reachable(start, goals, polygons, lo, hi, radius=0.25, cell=0.05):
    """Which goals can be reached from start on a grid inflated like the planner (BFS)."""
    from collections import deque
    nx, ny = int((hi[0] - lo[0]) / cell) + 1, int((hi[1] - lo[1]) / cell) + 1
    free = np.ones((nx, ny), dtype=bool)
    for poly in polygons:
        p = np.array(poly)
        i0, j0 = np.floor((p.min(0) - radius - lo) / cell).astype(int)
        i1, j1 = np.ceil((p.max(0) + radius - lo) / cell).astype(int)
        for i in range(max(i0, 0), min(i1, nx - 1) + 1):
            for j in range(max(j0, 0), min(j1, ny - 1) + 1):
                if free[i, j]:
                    x, y = lo[0] + i * cell, lo[1] + j * cell
                    if _inside(x, y, poly) or _dist(x, y, poly) <= radius:
                        free[i, j] = False

    def cell_of(q):
        return (int(round((q[0] - lo[0]) / cell)), int(round((q[1] - lo[1]) / cell)))
    seen = np.zeros_like(free)
    s0 = cell_of(start)
    queue = deque([s0])
    seen[s0] = True
    while queue:
        i, j = queue.popleft()
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            a, b = i + di, j + dj
            if 0 <= a < nx and 0 <= b < ny and free[a, b] and not seen[a, b]:
                seen[a, b] = True
                queue.append((a, b))
    return {name: bool(seen[cell_of(q)]) for name, q in goals.items()}


def _segments_cross(a, b, c, d):
    def orient(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return (orient(a, b, c) * orient(a, b, d) < 0) and (orient(c, d, a) * orient(c, d, b) < 0)


def _blocked(a, b, polygons):
    for poly in polygons:
        for i in range(len(poly)):
            if _segments_cross(a, b, poly[i], poly[(i + 1) % len(poly)]):
                return True
    return False


def place_in_front(poly, polygons, radius=0.4):
    """Navigation target next to a footprint: the nearest free spot on one of its four sides
    with a clear line to the furniture (not behind a wall)."""
    p = np.array(poly)
    (x0, y0), (x1, y1) = p.min(0), p.max(0)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    others = [q for q in polygons if q is not poly]
    for clearance in np.arange(0.4, 2.01, 0.1):
        for q, edge in (((x1 + clearance, cy), (x1, cy)), ((x0 - clearance, cy), (x0, cy)),
                        ((cx, y1 + clearance), (cx, y1)), ((cx, y0 - clearance), (cx, y0))):
            if is_free(q[0], q[1], polygons, radius) and not _blocked(edge, q, others):
                return [float(q[0]), float(q[1])]
    return None


def main(argv=None):
    """Convert the arena."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('usd')
    ap.add_argument('out_dir')
    ap.add_argument('map_yaml')
    args = ap.parse_args(argv)

    stage = Usd.Stage.Open(args.usd)
    objects = collect(stage)
    os.makedirs(os.path.join(args.out_dir, 'meshes'), exist_ok=True)

    assets, geoms, polygons, places = [], [], [], {}
    lo = np.array([np.inf, np.inf])
    hi = -lo
    for name, (verts, tris, rgb) in sorted(objects.items()):
        safe = _safe(name)
        v, t = _simplify(verts, tris, MAX_TRIS_PER_OBJECT)
        _write_obj(os.path.join(args.out_dir, 'meshes', f'{safe}.obj'), v, t)
        r, g, b = (min(1.0, max(0.0, c)) for c in rgb)
        # the USD floor/wall materials come out almost black: light wood floor, white walls
        if name in FLOOR_NAMES:
            r, g, b = 0.76, 0.62, 0.45
        elif re.match(r'^(Cube_\d+|Doorframe_\d+)$', name):
            r, g, b = 0.92, 0.92, 0.9
        assets.append(f'<mesh name="{safe}" file="meshes/{safe}.obj" inertia="shell"/>')
        assets.append(f'<material name="m_{safe}" rgba="{r:.3f} {g:.3f} {b:.3f} 1"/>')
        geoms.append(f'<geom name="v_{safe}" type="mesh" mesh="{safe}" material="m_{safe}" '
                     'contype="0" conaffinity="0" group="1"/>')
        if name in FLOOR_NAMES:
            continue
        hulls = footprints(v, t)
        for k, box in enumerate(hulls):
            pts = np.array(box)
            lo, hi = np.minimum(lo, pts.min(0)), np.maximum(hi, pts.max(0))
            polygons.append({'name': name if k == 0 else f'{name}#{k}', 'type': 'obstacle',
                             'frame': 'map', 'color': 'red',
                             'points': [[round(float(x), 3), round(float(y), 3)]
                                        for x, y in box]})
        print(f'{name:40s} {len(tris):7d} -> {len(t):6d} tris, '
              f'{len(hulls)} obstacle part(s)')

    # map = walls and furniture plus a margin
    lo, hi = lo - MAP_MARGIN_M, hi + MAP_MARGIN_M
    center = ((lo + hi) / 2).tolist()
    by_name = {p['name']: p['points'] for p in polygons}
    all_polys = list(by_name.values())
    for pattern, place in PLACES:
        for name, box in by_name.items():
            if re.match(pattern, name):
                q = place_in_front(box, all_polys)
                if q is None:
                    print(f'place {place}: no free spot in front of {name}, skipped')
                    continue
                places[place] = {'type': 'place', 'frame': 'map',
                                 'position': [round(q[0], 3), round(q[1], 3)]}
    # start of the simulated robot: free spot nearest to the centre (type sim_start: drive
    # server treats type 'start' as an odom offset, the simulator already uses map coordinates)
    def free(x, y):
        return is_free(x, y, all_polys, 0.45)
    cands = sorted(((x, y) for x in np.arange(lo[0] + 0.6, hi[0] - 0.6, 0.1)
                    for y in np.arange(lo[1] + 0.6, hi[1] - 0.6, 0.1)),
                   key=lambda q: math.hypot(q[0] - center[0], q[1] - center[1]))
    start = next((q for q in cands if free(*q)), center)
    places['Start'] = {'type': 'sim_start', 'frame': 'map',
                       'position': [round(float(start[0]), 3), round(float(start[1]), 3)]}
    # 'Mitte' = the free start spot near the centre (the exact centre is furniture)
    places['Mitte'] = {'type': 'place', 'frame': 'map', 'position': places['Start']['position']}
    goals = {n: o['position'] for n, o in places.items()}
    for name, ok in reachable(start, goals, all_polys, lo, hi).items():
        if not ok:
            print(f'place {name}: not reachable from the start (inflated like the planner)')

    with open(os.path.join(args.out_dir, 'arena_visuals.xml'), 'w', encoding='utf-8') as f:
        f.write('<mujocoinclude>\n  <asset>\n    ' + '\n    '.join(assets) +
                '\n  </asset>\n  <worldbody>\n    ' + '\n    '.join(geoms) +
                '\n  </worldbody>\n</mujocoinclude>\n')

    res = 0.05
    doc = {
        'map': {'resolution': res, 'origin': [round(float(lo[0]), 3), round(float(lo[1]), 3)],
                'width_px': int(math.ceil((hi[0] - lo[0]) / res)),
                'height_px': int(math.ceil((hi[1] - lo[1]) / res)),
                'width_m': round(float(hi[0] - lo[0]), 3),
                'height_m': round(float(hi[1] - lo[1]), 3),
                'source': 'RoboCup@Home arena (Competition_Arena_AtHome.usdc), '
                          'pkg_sim/tools/arena_convert.py'},
        'objects': places,
        'polygons': polygons + [{
            'name': 'Arena', 'type': 'boundary', 'frame': 'map', 'color': 'orange',
            'points': [[round(float(lo[0]), 3), round(float(lo[1]), 3)],
                       [round(float(hi[0]), 3), round(float(lo[1]), 3)],
                       [round(float(hi[0]), 3), round(float(hi[1]), 3)],
                       [round(float(lo[0]), 3), round(float(hi[1]), 3)]]}],
    }
    with open(args.map_yaml, 'w', encoding='utf-8') as f:
        f.write('# Generated by pkg_sim/tools/arena_convert.py from the RoboCup@Home arena USD.\n'
                '# Obstacles = footprints (below 1 m) of walls and furniture; objects = places in\n'
                '# front of the furniture (navigation targets). Do not edit by hand.\n')
        yaml.safe_dump(doc, f, sort_keys=False, allow_unicode=True)
    print(f'{len(objects)} objects, {len(polygons)} obstacles, places: {", ".join(places)}')


if __name__ == '__main__':
    main()
