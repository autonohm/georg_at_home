"""Convert the pib web robot model (pib-3d release zip) into a URDF.

The release zip of github.com/pib-rocks/pib-3d (the model Cerebra shows) contains
model.json (links with one GLB mesh each, joints with parent/child/origin/axis/limit),
mapping.json (motor -> URDF joint) and meshes/*.glb. model.json is already a URDF tree in
JSON form, reduced to 47 links, so the conversion is mechanical.

    python3 -m pib_model.convert <bundle dir> <out dir> [--package pib_model]

writes <out dir>/pib.urdf and copies meshes/ and mapping.json next to it.
"""
import argparse
import json
import math
import os
import shutil
import struct
import xml.etree.ElementTree as ET

ROOT_LINK = 'root'
# visual origin of GLB meshes: undoes the y-up -> z-up turn of glTF viewers (Lichtblick)
GLB_VISUAL_RPY = f'{-math.pi / 2:.9g} 0 0'


def _fmt(values):
    return ' '.join(f'{v:.9g}' for v in values)


def load_bundle(bundle_dir):
    """Return (model, mapping, version) of an unpacked release bundle."""
    def load(name):
        with open(os.path.join(bundle_dir, name), encoding='utf-8') as f:
            return json.load(f)
    return load('model.json'), load('mapping.json'), load('version.json')


def model_to_urdf(model, package='pib_model', robot_name='pib', model_dir='model'):
    """Build the URDF XML string from model.json.

    Mesh URIs: package://<package>/<model_dir>/meshes/... - setup.py installs the converted
    model into share/<package>/<model_dir>/.
    """
    robot = ET.Element('robot', name=robot_name)
    # some joints connect links without a mesh, which model.json does not list: add them empty
    listed = {link['name'] for link in model['links']}
    used = [n for j in model['joints'] for n in (j['parent'], j['child'])]
    extra = [{'name': n} for n in dict.fromkeys(used) if n not in listed]
    for link in model['links'] + extra:
        el = ET.SubElement(robot, 'link', name=link['name'])
        if link.get('mesh'):
            visual = ET.SubElement(el, 'visual')
            # The GLBs of pib-3d hold ROS coordinates (z up; Cerebra turns the whole robot by
            # -90 deg about x into its y-up three.js scene). Lichtblick treats GLB as glTF
            # (y up) and turns every GLB by +90 deg about x - always, its setting "Mesh up
            # axis" only applies to STL/OBJ. Undo that here; without it the parts that lie
            # away from their link origin fly apart (seen in Lichtblick 1.30 on 2026-11-21).
            rpy = GLB_VISUAL_RPY if link['mesh'].lower().endswith('.glb') else '0 0 0'
            ET.SubElement(visual, 'origin', xyz='0 0 0', rpy=rpy)
            geom = ET.SubElement(visual, 'geometry')
            ET.SubElement(geom, 'mesh', filename=f'package://{package}/{model_dir}/{link["mesh"]}')
    for joint in model['joints']:
        el = ET.SubElement(robot, 'joint', name=joint['name'], type=joint['type'])
        ET.SubElement(el, 'parent', link=joint['parent'])
        ET.SubElement(el, 'child', link=joint['child'])
        origin = joint.get('origin', {})
        ET.SubElement(el, 'origin', xyz=_fmt(origin.get('xyz', [0, 0, 0])),
                      rpy=_fmt(origin.get('rpy', [0, 0, 0])))
        if joint['type'] != 'fixed':
            ET.SubElement(el, 'axis', xyz=_fmt(joint.get('axis', [0, 0, 1])))
        if joint['type'] in ('revolute', 'prismatic'):
            limit = joint.get('limit') or {}
            ET.SubElement(el, 'limit', lower=f'{limit.get("lower", -math.pi):.9g}',
                          upper=f'{limit.get("upper", math.pi):.9g}', effort='1', velocity='2')
    ET.indent(robot)
    return '<?xml version="1.0"?>\n' + ET.tostring(robot, encoding='unicode') + '\n'


def glb_bounds(path):
    """Axis-aligned bounds (min, max) of all POSITION accessors of a GLB, in mesh units."""
    with open(path, 'rb') as f:
        data = f.read()
    magic, _version, _length = struct.unpack('<4sII', data[:12])
    if magic != b'glTF':
        raise ValueError(f'{path}: not a GLB file')
    chunk_len, chunk_type = struct.unpack('<II', data[12:20])
    if chunk_type != 0x4E4F534A:  # 'JSON'
        raise ValueError(f'{path}: first chunk is not JSON')
    gltf = json.loads(data[20:20 + chunk_len])
    lo, hi = [math.inf] * 3, [-math.inf] * 3
    for mesh in gltf.get('meshes', []):
        for prim in mesh.get('primitives', []):
            acc = gltf['accessors'][prim['attributes']['POSITION']]
            for i in range(3):
                lo[i] = min(lo[i], acc['min'][i])
                hi[i] = max(hi[i], acc['max'][i])
    return lo, hi


def triangle_count(path):
    """Count the triangles of a GLB (from the index or position accessor counts)."""
    with open(path, 'rb') as f:
        data = f.read()
    chunk_len = struct.unpack('<I', data[12:16])[0]
    gltf = json.loads(data[20:20 + chunk_len])
    total = 0
    for mesh in gltf.get('meshes', []):
        for prim in mesh.get('primitives', []):
            idx = prim.get('indices')
            count = gltf['accessors'][idx if idx is not None
                                      else prim['attributes']['POSITION']]['count']
            total += count // 3
    return total


# --- small homogeneous-transform helpers (no numpy needed) ------------------------------

def _rpy_matrix(roll, pitch, yaw):
    cr, sr, cp, sp, cy, sy = (math.cos(roll), math.sin(roll), math.cos(pitch),
                              math.sin(pitch), math.cos(yaw), math.sin(yaw))
    return [[cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr],
            [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr],
            [-sp, cp * sr, cp * cr]]


def _transform(xyz, rpy):
    r = _rpy_matrix(*rpy)
    return [r[0] + [xyz[0]], r[1] + [xyz[1]], r[2] + [xyz[2]], [0, 0, 0, 1]]


def _mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]


def _apply(t, p):
    return [t[i][0] * p[0] + t[i][1] * p[1] + t[i][2] * p[2] + t[i][3] for i in range(3)]


def zero_pose_link_transforms(model):
    """World transform of every link with all joints at 0 (root = identity)."""
    children = {}
    for joint in model['joints']:
        children.setdefault(joint['parent'], []).append(joint)
    world = {ROOT_LINK: _transform([0, 0, 0], [0, 0, 0])}
    stack = [ROOT_LINK]
    while stack:
        parent = stack.pop()
        for joint in children.get(parent, []):
            o = joint.get('origin', {})
            local = _transform(o.get('xyz', [0, 0, 0]), o.get('rpy', [0, 0, 0]))
            world[joint['child']] = _mul(world[parent], local)
            stack.append(joint['child'])
    return world


def zero_pose_bounds(model, bundle_dir):
    """World bounds of every link mesh in the zero pose: {link: (min, max)}."""
    world = zero_pose_link_transforms(model)
    result = {}
    for link in model['links']:
        if not link.get('mesh') or link['name'] not in world:
            continue
        lo, hi = glb_bounds(os.path.join(bundle_dir, link['mesh']))
        corners = [[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1])
                   for z in (lo[2], hi[2])]
        pts = [_apply(world[link['name']], c) for c in corners]
        result[link['name']] = ([min(p[i] for p in pts) for i in range(3)],
                                [max(p[i] for p in pts) for i in range(3)])
    return result


def main(argv=None):
    """Command line: convert a bundle directory into <out>/pib.urdf + meshes + mapping."""
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('bundle')
    parser.add_argument('out')
    parser.add_argument('--package', default='pib_model')
    args = parser.parse_args(argv)
    model, _mapping, version = load_bundle(args.bundle)
    os.makedirs(args.out, exist_ok=True)
    with open(os.path.join(args.out, 'pib.urdf'), 'w', encoding='utf-8') as f:
        f.write(model_to_urdf(model, args.package))
    shutil.copytree(os.path.join(args.bundle, 'meshes'), os.path.join(args.out, 'meshes'),
                    dirs_exist_ok=True)
    for name in ('mapping.json', 'version.json'):
        shutil.copy(os.path.join(args.bundle, name), os.path.join(args.out, name))
    print(f'pib model {version.get("version")}: {len(model["links"])} links, '
          f'{len(model["joints"])} joints -> {args.out}')


if __name__ == '__main__':
    main()
