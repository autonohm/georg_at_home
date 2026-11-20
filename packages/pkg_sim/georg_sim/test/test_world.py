import math
import os

from georg_sim.world import World
import pytest

MAP = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                   'pkg_slam', 'maps', 'Nav_Test.yaml')


@pytest.fixture(scope='module')
def world():
    return World.from_yaml(MAP)


def square_world():
    box = [(0.0, 0.0), (4.0, 0.0), (4.0, 4.0), (0.0, 4.0)]
    pillar = [(1.8, 1.8), (2.2, 1.8), (2.2, 2.2), (1.8, 2.2)]
    return World(box, [pillar], [], {})


def test_raycast_hits_the_nearest_wall():
    w = square_world()
    assert w.raycast((1.0, 2.0), 0.0, 10.0) == pytest.approx(0.8)      # pillar
    assert w.raycast((1.0, 2.0), math.pi, 10.0) == pytest.approx(1.0)  # left wall
    assert w.raycast((1.0, 2.0), 0.0, 0.5) == math.inf                 # beyond range


def test_free_space_respects_walls_obstacles_and_radius():
    w = square_world()
    assert w.is_free((1.0, 1.0), 0.3)
    assert not w.is_free((2.0, 2.0))          # inside the pillar
    assert not w.is_free((5.0, 1.0))          # outside the arena
    assert not w.is_free((0.2, 1.0), 0.3)     # too close to the wall


def test_scan_has_one_range_per_beam():
    ranges = square_world().scan(1.0, 2.0, 0.0, 360, 10.0)
    assert len(ranges) == 360
    assert ranges[180] == pytest.approx(0.8)  # beam 180 points forward


def test_nav_test_map_loads_and_objects_are_reachable(world):
    assert world.boundary and world.solids
    assert set(world.objects) == {'Door', 'Seat'}
    assert world.is_free((1.0, 0.1), 0.25)    # default start pose of the simulator
