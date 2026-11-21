"""Combined robot description for display: Georg (georg_description) + movable pib.

georg_description shows pib as one rigid mesh (pib_4S.stl) on pib_waist_link. For Lichtblick
we take Georg's URDF as published by pkg_urdf, drop that rigid mesh and add the links of the
pib URDF (fixed joint pib_waist_link -> root). Nothing in pkg_urdf changes.
"""
import xml.etree.ElementTree as ET


def _rpy_str(values):
    return ' '.join(f'{v:.9g}' for v in values)


def combine(georg_urdf, pib_urdf, waist_link='pib_waist_link', root_link='root',
            xyz=(0.0, 0.0, 0.0), rpy=(0.0, 0.0, 0.0), hide_mesh='pib_4S.stl'):
    """Return the combined URDF string (rigid pib mesh removed, pib links attached)."""
    georg = ET.fromstring(georg_urdf)
    pib = ET.fromstring(pib_urdf)
    for link in georg.findall('link'):
        for visual in list(link.findall('visual')):
            mesh = visual.find('geometry/mesh')
            if mesh is not None and hide_mesh and hide_mesh in mesh.get('filename', ''):
                link.remove(visual)
    names = {link.get('name') for link in georg.findall('link')}
    clash = names & {link.get('name') for link in pib.findall('link')}
    if clash:
        raise ValueError(f'pib links already exist in the Georg model: {sorted(clash)}')
    for el in list(pib):
        if el.tag in ('link', 'joint'):
            georg.append(el)
    joint = ET.SubElement(georg, 'joint', name='pib_mount_joint', type='fixed')
    ET.SubElement(joint, 'parent', link=waist_link)
    ET.SubElement(joint, 'child', link=root_link)
    ET.SubElement(joint, 'origin', xyz=_rpy_str(xyz), rpy=_rpy_str(rpy))
    return '<?xml version="1.0"?>\n' + ET.tostring(georg, encoding='unicode')
