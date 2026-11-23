import os

from georg_sim import worlds

MAPS = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'pkg_slam', 'maps')


def test_worlds_are_the_map_yamls_with_polygons():
    names = worlds.list_worlds(MAPS)
    assert 'Nav_Test.yaml' in names and 'Wohnung.yaml' in names
    assert all(n.endswith('.yaml') for n in names)


def test_resolve_accepts_names_and_rejects_unknown_worlds():
    assert worlds.resolve('Wohnung', MAPS).endswith('/Wohnung.yaml')
    assert worlds.resolve('/elsewhere/Wohnung.yaml', MAPS).endswith('/Wohnung.yaml')
    assert worlds.resolve('Nope.yaml', MAPS) is None
    assert worlds.resolve('', MAPS) is None


def test_visuals_next_to_the_map():
    assert worlds.visuals_for(os.path.join(MAPS, 'Wohnung.yaml')).endswith('Wohnung_visuals.xml')
    assert worlds.visuals_for(os.path.join(MAPS, 'Nav_Test.yaml')) == ''
