"""Validator: only catalog tasks with valid arguments get through.

Two entry points:

- ``validate_plan``: checks a plan as the LLM will send it from P6,
  ``[{"task": "gesture", "args": {...}}, ...]``.
- ``check_mission``: checks a mission written in Python (``missions/*.py``):
  every task object must be an instance of a catalog class.

No ROS imports here.
"""

from dataclasses import dataclass, field
from typing import Iterable, List, Tuple

from georg_task_manager.catalog import Catalog, TaskSpec

PRIORITIES = ('low', 'mid', 'high', 'critical')
DEFAULT_MAX_STEPS = 20


@dataclass
class ValidationResult:
    ok: bool
    errors: List[str] = field(default_factory=list)
    steps: List[Tuple[str, dict]] = field(default_factory=list)


def _check_value(task: str, arg: str, value, schema: dict) -> List[str]:
    kind = schema['type']
    where = f'{task}.{arg}'
    if kind == 'string' and not isinstance(value, str):
        return [f'{where}: expected string, got {type(value).__name__}']
    if kind == 'boolean' and not isinstance(value, bool):
        return [f'{where}: expected boolean, got {type(value).__name__}']
    if kind == 'integer' and (isinstance(value, bool) or not isinstance(value, int)):
        return [f'{where}: expected integer, got {type(value).__name__}']
    if kind == 'number' and (isinstance(value, bool) or not isinstance(value, (int, float))):
        return [f'{where}: expected number, got {type(value).__name__}']
    errors = []
    if 'enum' in schema and value not in schema['enum']:
        errors.append(f"{where}: '{value}' not in {schema['enum']}")
    if 'min' in schema and value < schema['min']:
        errors.append(f"{where}: {value} < min {schema['min']}")
    if 'max' in schema and value > schema['max']:
        errors.append(f"{where}: {value} > max {schema['max']}")
    return errors


def check_args(spec: TaskSpec, args: dict) -> List[str]:
    errors = []
    for arg, value in args.items():
        if arg == 'priority':
            if value not in PRIORITIES:
                errors.append(f"{spec.name}.priority: '{value}' not in {list(PRIORITIES)}")
            continue
        schema = spec.args_schema.get(arg)
        if schema is None:
            errors.append(f"{spec.name}: unknown argument '{arg}'")
            continue
        errors += _check_value(spec.name, arg, value, schema)
    for arg, schema in spec.args_schema.items():
        if schema.get('required', True) and arg not in args:
            errors.append(f"{spec.name}: missing argument '{arg}'")
    return errors


def validate_plan(plan, catalog: Catalog, mode: str, satisfied: Iterable[str] = (),
                  max_steps: int = DEFAULT_MAX_STEPS) -> ValidationResult:
    """Check a plan against the catalog. Returns all errors, not just the first."""
    errors: List[str] = []
    steps: List[Tuple[str, dict]] = []
    satisfied = set(satisfied)

    if not isinstance(plan, list):
        return ValidationResult(False, ['plan must be a list'])
    if not plan:
        return ValidationResult(False, ['plan is empty'])
    if len(plan) > max_steps:
        errors.append(f'plan has {len(plan)} steps, maximum is {max_steps}')

    for i, step in enumerate(plan):
        prefix = f'step {i}'
        if not isinstance(step, dict) or 'task' not in step:
            errors.append(f'{prefix}: needs the form {{task, args}}')
            continue
        extra = set(step) - {'task', 'args'}
        if extra:
            errors.append(f'{prefix}: unknown keys {sorted(extra)}')
        name = step['task']
        spec = catalog.tasks.get(name) if isinstance(name, str) else None
        if spec is None:
            errors.append(f"{prefix}: unknown task '{name}'")
            continue
        args = step.get('args', {}) or {}
        if not isinstance(args, dict):
            errors.append(f'{prefix}: args must be an object')
            continue
        if mode not in spec.modes:
            errors.append(f"{prefix}: task '{name}' not allowed in mode '{mode}'")
        missing = [r for r in spec.requires if r not in satisfied]
        if missing:
            errors.append(f"{prefix}: task '{name}' requires {missing}")
        errors += [f'{prefix}: {e}' for e in check_args(spec, args)]
        steps.append((name, dict(args)))

    return ValidationResult(not errors, errors, steps if not errors else [])


def instantiate(steps: List[Tuple[str, dict]], catalog: Catalog) -> List[object]:
    """Turn validated steps into task objects (imports the task classes)."""
    from georg_task_manager.tasks.priority import TaskPriority

    tasks = []
    for name, args in steps:
        args = dict(args)
        if 'priority' in args:
            args['priority'] = TaskPriority(args['priority'])
        tasks.append(catalog.tasks[name].load_class()(**args))
    return tasks


def check_mission(tasks, catalog: Catalog) -> List[str]:
    """Every task of a Python mission must be a catalog class."""
    errors = []
    if not tasks:
        return ['mission has no tasks']
    for i, task in enumerate(tasks):
        if catalog.by_class(type(task)) is None:
            name = getattr(task, 'name', type(task).__name__)
            cls = f'{type(task).__module__}.{type(task).__name__}'
            errors.append(f'task {i} ({name}): class {cls} is not in the catalog')
    return errors
