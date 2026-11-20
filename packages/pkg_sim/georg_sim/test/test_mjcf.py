import math
import os

from georg_sim.mjcf import build_mjcf
from georg_sim.world import World
import pytest

mujoco = pytest.importorskip('mujoco')
np = pytest.importorskip('numpy')

MAP = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                   'pkg_slam', 'maps', 'Nav_Test.yaml')


@pytest.fixture(scope='module')
def model_and_data():
    world = World.from_yaml(MAP)
    model = mujoco.MjModel.from_xml_string(build_mjcf(world, (1.0, 0.1, 0.0), 0.2))
    data = mujoco.MjData(model)
    mujoco.mj_resetDataKeyframe(model, data, 0)
    mujoco.mj_forward(model, data)
    return world, model, data


def _drive(model, data, vx, vy, wz, seconds):
    data.ctrl[:] = [vx, vy, wz]
    for _ in range(int(seconds / model.opt.timestep)):
        mujoco.mj_step(model, data)


def test_model_has_walls_and_starts_at_the_start_pose(model_and_data):
    world, model, data = model_and_data
    assert model.ngeom >= len(world.segments)
    assert data.qpos[:3] == pytest.approx([1.0, 0.1, 0.0])


def test_robot_drives_and_is_stopped_by_a_wall(model_and_data):
    world, model, data = model_and_data
    _drive(model, data, 0.3, 0.0, 0.0, 1.0)
    assert 0.2 < data.qpos[0] - 1.0 < 0.4                  # it drives
    _drive(model, data, 0.0, 1.0, 0.0, 6.0)                # towards TV / Wall1 at y >= 1.44
    assert data.qpos[1] < 1.44 - 0.2 + 0.03                 # radius 0.2, walls are solid
    assert world.is_free((data.qpos[0], data.qpos[1]))


def test_mujoco_laser_matches_the_2d_laser(model_and_data):
    world, model, data = model_and_data
    mujoco.mj_resetDataKeyframe(model, data, 0)
    mujoco.mj_forward(model, data)
    body = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_BODY, 'base')
    origin = np.array([1.0, 0.1, 0.25])
    for angle in (0.0, math.pi / 2, math.pi, -math.pi / 2):
        vec = np.array([math.cos(angle), math.sin(angle), 0.0])
        geomid = np.zeros(1, dtype=np.int32)
        mj = mujoco.mj_ray(model, data, origin, vec, None, 1, body, geomid)
        flat = world.raycast((1.0, 0.1), angle, 20.0)
        assert mj == pytest.approx(flat, abs=0.03)           # walls are 5 cm thick boxes
