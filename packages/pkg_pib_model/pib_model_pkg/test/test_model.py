"""Tests without ROS: conversion, joint mapping, combined description."""
import math
import os
import xml.etree.ElementTree as ET

from pib_model.convert import model_to_urdf, zero_pose_link_transforms
from pib_model.description import combine
from pib_model.mapping import MotorMapping
import pytest

MODEL = {
    'links': [{'name': 'root', 'mesh': 'meshes/root.glb'},
              {'name': 'arm', 'mesh': 'meshes/arm.glb'}],
    'joints': [
        {'name': 'shoulder', 'type': 'revolute', 'parent': 'root', 'child': 'arm',
         'origin': {'xyz': [0.1, 0.0, 0.2], 'rpy': [0.0, 0.0, math.pi / 2]},
         'axis': [0, 1, 0], 'limit': {'lower': -1.0, 'upper': 1.0}},
        # a joint to a link without mesh, which model.json does not list
        {'name': 'tip', 'type': 'fixed', 'parent': 'arm', 'child': 'arm_tip',
         'origin': {'xyz': [0.0, 0.3, 0.0], 'rpy': [0, 0, 0]}},
    ],
}

MAPPING = {'joints': [
    {'urdfJoint': 'shoulder', 'motor': 'shoulder_vertical_left', 'class': 'driven',
     'direction': -1, 'gearRatio': 1.0, 'zeroOffsetDeg': 10.0},
    {'urdfJoint': 'knuckle', 'motor': 'index_left_stretch', 'class': 'driven',
     'direction': 1, 'gearRatio': 2.0, 'zeroOffsetDeg': 0.0},
    {'urdfJoint': 'middle', 'motor': None, 'class': 'coupled',
     'coupling': {'follows': 'knuckle', 'factor': 1.0}},
    {'urdfJoint': 'tip', 'motor': None, 'class': 'coupled',
     'coupling': {'follows': 'middle', 'factor': -1.0}},
    {'urdfJoint': 'lid', 'motor': None, 'class': 'passive'},
]}

GEORG = """<robot name="georg">
  <link name="base_link"/>
  <link name="pib_waist_link"><visual><geometry>
    <mesh filename="package://georg_description/meshes/pib_4S.stl"/></geometry></visual></link>
  <joint name="pib_waist_joint" type="fixed"><parent link="base_link"/>
    <child link="pib_waist_link"/></joint>
</robot>"""


def test_urdf_has_all_links_joints_and_mesh_uris():
    root = ET.fromstring(model_to_urdf(MODEL, 'pib_model'))
    assert {link.get('name') for link in root.findall('link')} == {'root', 'arm', 'arm_tip'}
    shoulder = root.find("joint[@name='shoulder']")
    assert shoulder.get('type') == 'revolute'
    assert shoulder.find('limit').get('lower') == '-1'
    assert root.find("link[@name='arm']/visual/geometry/mesh").get('filename') == \
        'package://pib_model/meshes/arm.glb'


def test_zero_pose_follows_the_joint_origins():
    world = zero_pose_link_transforms(MODEL)
    tip = world['arm_tip']
    # yaw 90 deg at the shoulder turns the 0.3 m along y of the tip into -x
    assert tip[0][3] == pytest.approx(0.1 - 0.3)
    assert tip[2][3] == pytest.approx(0.2)


def test_motor_angles_like_cerebra():
    m = MotorMapping(MAPPING)
    # urdf_deg = motor_deg * gear * direction - offset: 30 deg -> -30 - 10 = -40 deg
    assert m.motor_to_joint_rad('shoulder_vertical_left', 3000) == \
        pytest.approx(math.radians(-40))
    back = m.joint_rad_to_motor_centideg('shoulder_vertical_left', math.radians(-40))
    assert back == pytest.approx(3000)


def test_coupled_joints_follow_and_passive_stay_zero():
    pos = MotorMapping(MAPPING).joint_positions({'index_left_stretch': 1500, 'unknown': 9})
    assert pos['knuckle'] == pytest.approx(math.radians(30))
    assert pos['middle'] == pytest.approx(math.radians(30))
    assert pos['tip'] == pytest.approx(math.radians(-30))
    assert pos['lid'] == 0.0
    assert pos['shoulder'] == 0.0                     # motor not reported: joint stays at 0
    with_zero = MotorMapping(MAPPING).joint_positions({'shoulder_vertical_left': 0})
    assert with_zero['shoulder'] == pytest.approx(math.radians(-10))   # 0 -> -offset


def test_combined_description_drops_rigid_pib_and_mounts_the_model():
    full = ET.fromstring(combine(GEORG, model_to_urdf(MODEL), xyz=(0.1, 0, 0.6),
                                 rpy=(0, 0, math.pi / 2)))
    meshes = [m.get('filename') for m in full.iter('mesh')]
    assert not any('pib_4S.stl' in m for m in meshes)
    assert 'package://pib_model/meshes/arm.glb' in meshes
    mount = full.find("joint[@name='pib_mount_joint']")
    assert mount.find('parent').get('link') == 'pib_waist_link'
    assert mount.find('child').get('link') == 'root'


def test_link_name_clash_is_refused():
    with pytest.raises(ValueError):
        combine(GEORG, GEORG.replace('georg', 'pib'))


REAL_MAPPING = os.environ.get('PIB_MODEL_DIR')


@pytest.mark.skipif(not REAL_MAPPING, reason='set PIB_MODEL_DIR to the converted model')
def test_real_mapping_covers_every_motor_of_pib_backend():
    import json
    with open(os.path.join(REAL_MAPPING, 'mapping.json'), encoding='utf-8') as f:
        m = MotorMapping(json.load(f))
    assert len(m.motor_names) == 26
    for motor in ('shoulder_vertical_left', 'elbow_right', 'turn_head_motor'):
        assert motor in m.motor_names
    with open(os.path.join(REAL_MAPPING, 'pib.urdf'), encoding='utf-8') as f:
        urdf = ET.fromstring(f.read())
    joints = {j.get('name') for j in urdf.findall('joint')}
    assert set(m.joint_names()) <= joints
