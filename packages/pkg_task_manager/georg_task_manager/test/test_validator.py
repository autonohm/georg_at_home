"""Catalog and validator: only catalog tasks with valid arguments get through."""

from georg_task_manager.catalog import CatalogError, load_catalog
from georg_task_manager.missions import DigitalFestival, Test_Mapping
from georg_task_manager.validator import check_mission, instantiate, validate_plan
import pytest


@pytest.fixture(scope='module')
def catalog():
    return load_catalog()


GESTURE = {'mode': 'look_at', 'vx': 0, 'vy': 0, 'vz': 0}


def ok_plan():
    return [
        {'task': 'listen', 'args': {'sound': 'DOORBELL', 'priority': 'high'}},
        {'task': 'gesture', 'args': {'mode': 'look_at', 'vx': -1000.0, 'vy': 0, 'vz': 100.0}},
        {'task': 'return_to_idle'},
    ]


def test_catalog_loads_and_classes_exist(catalog):
    expected = {'listen', 'gesture', 'navigate_object', 'navigate_room', 'return_to_idle'}
    assert expected <= set(catalog.tasks)
    for spec in catalog.tasks.values():
        assert spec.load_class() is not None


def test_valid_plan_passes(catalog):
    result = validate_plan(ok_plan(), catalog, mode='mock')
    assert result.ok, result.errors
    assert [name for name, _ in result.steps] == ['listen', 'gesture', 'return_to_idle']


def test_valid_plan_can_be_turned_into_tasks(catalog):
    tasks = instantiate(validate_plan(ok_plan(), catalog, mode='mock').steps, catalog)
    assert [t.name for t in tasks] == ['Listening(DOORBELL)', 'Gesture', 'ReturnToIdle']
    assert tasks[0].priority.value == 'high'
    assert check_mission(tasks, catalog) == []


@pytest.mark.parametrize('plan, expected', [
    ([{'task': 'fly_away'}], "unknown task 'fly_away'"),
    ([{'task': 'gesture', 'args': GESTURE | {'mode': 'dance'}}], 'not in'),
    ([{'task': 'gesture', 'args': GESTURE | {'vx': 'far'}}], 'expected number'),
    ([{'task': 'gesture', 'args': GESTURE | {'vx': True}}], 'expected number'),
    ([{'task': 'gesture', 'args': {'mode': 'look_at', 'vx': 0, 'vy': 0}}], 'missing argument'),
    ([{'task': 'listen', 'args': {'sound': 'SPEECH', 'volume': 3}}], "unknown argument 'volume'"),
    ([{'task': 'listen', 'args': {'sound': 'SPEECH', 'timeout_sec': -1}}], '< min'),
    ([{'task': 'listen', 'args': {'sound': 'SPEECH', 'priority': 'urgent'}}], 'priority'),
    ([{'task': 'listen', 'args': 'SPEECH'}], 'args must be an object'),
    ([{'task': 'listen', 'args': {'sound': 'SPEECH'}, 'why': 'x'}], 'unknown keys'),
    (['listen'], '{task, args}'),
    ([], 'plan is empty'),
    ({'task': 'listen'}, 'plan must be a list'),
])
def test_invalid_plans_are_rejected(catalog, plan, expected):
    result = validate_plan(plan, catalog, mode='mock')
    assert not result.ok
    assert result.steps == []
    assert any(expected in e for e in result.errors), result.errors


def test_too_long_plan_is_rejected(catalog):
    result = validate_plan([{'task': 'return_to_idle'}] * 5, catalog, mode='mock', max_steps=4)
    assert not result.ok and 'maximum is 4' in result.errors[0]


def test_mode_and_preconditions_are_checked(catalog):
    catalog.tasks['navigate_object'].requires.append('slam_ready')
    catalog.tasks['navigate_object'].modes.remove('mcap')
    try:
        args = {'object_name': 'Seat', 'map_path': '/m.yaml'}
        plan = [{'task': 'navigate_object', 'args': args}]
        errors = validate_plan(plan, catalog, 'sim').errors
        assert any("requires ['slam_ready']" in e for e in errors)
        assert validate_plan(plan, catalog, 'sim', satisfied={'slam_ready'}).ok
        errors = validate_plan(plan, catalog, 'mcap', satisfied={'slam_ready'}).errors
        assert any("not allowed in mode 'mcap'" in e for e in errors)
    finally:
        catalog.tasks['navigate_object'].requires.remove('slam_ready')
        catalog.tasks['navigate_object'].modes.append('mcap')


def test_existing_missions_only_use_catalog_tasks(catalog):
    assert check_mission(DigitalFestival.get_mission(), catalog) == []
    assert check_mission(Test_Mapping.get_mission(), catalog) == []


def test_broken_catalog_is_reported(tmp_path):
    bad = tmp_path / 'catalog.yaml'
    bad.write_text('tasks:\n  x:\n    class: a:B\n    args_schema: {n: {type: float}}\n'
                   '    timeout_s: 1\n    modes: [mock]\n')
    with pytest.raises(CatalogError, match='needs a type'):
        load_catalog(str(bad))


def test_name_arg_must_be_an_argument(tmp_path):
    bad = tmp_path / 'catalog.yaml'
    bad.write_text('tasks:\n  x:\n    class: a:B\n    args_schema: {n: {type: number}}\n'
                   '    timeout_s: 1\n    modes: [mock]\n    name_arg: m\n')
    with pytest.raises(CatalogError, match='name_arg'):
        load_catalog(str(bad))


def test_blocks_are_loaded_and_validated(catalog):
    assert {'greet_guest', 'wait_for_guest'} <= set(catalog.blocks)
    assert all(spec.description for spec in catalog.tasks.values())
    plan = [{'block': 'wait_for_guest'}, {'block': 'greet_guest'},
            {'task': 'navigate_object', 'args': {'object_name': 'Seat'}}]
    result = validate_plan(plan, catalog, mode='mock')
    assert result.ok, result.errors
    assert result.items[0] == {'block': 'wait_for_guest'}
    assert result.items[2] == {'task': 'navigate_object', 'args': {'object_name': 'Seat'}}


@pytest.mark.parametrize('plan, expected', [
    ([{'block': 'dance'}], "unknown block 'dance'"),
    ([{'block': 'greet_guest', 'args': {'loud': True}}], 'takes no arguments'),
    ([{'block': 'greet_guest', 'why': 1}], 'unknown keys'),
])
def test_invalid_blocks_are_rejected(catalog, plan, expected):
    result = validate_plan(plan, catalog, mode='mock')
    assert not result.ok and any(expected in e for e in result.errors), result.errors


def test_block_tasks_are_built(catalog):
    from georg_task_manager.validator import block_tasks
    tasks = block_tasks('greet_guest', catalog)
    assert [t.mode for t in tasks] == ['look_at', 'point_to', 'greet_person']


def test_integer_numbers_become_floats_for_ros(catalog):
    # the LLM writes 60, the ROS message needs 60.0 (float32 field)
    tasks = instantiate([('listen', {'sound': 'DOORBELL', 'timeout_sec': 60}),
                         ('gesture', {'mode': 'look_at', 'vx': 0, 'vy': 1, 'vz': 2})], catalog)
    assert isinstance(tasks[0].timeout_sec, float) and tasks[0].timeout_sec == 60.0
    assert all(isinstance(v, float) for v in (tasks[1].vx, tasks[1].vy, tasks[1].vz))
