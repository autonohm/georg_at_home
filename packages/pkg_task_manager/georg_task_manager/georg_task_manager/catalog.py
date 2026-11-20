"""Loads catalog.yaml. No ROS imports here."""

from dataclasses import dataclass, field
import importlib
import os
from typing import Dict, List

import yaml

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'catalog.yaml')
TYPES = ('string', 'number', 'integer', 'boolean')


@dataclass
class TaskSpec:
    name: str
    class_path: str
    action: str
    type: str  # noqa: A003  (same key as in catalog.yaml)
    args_schema: Dict[str, dict]
    timeout_s: float
    cancelable: bool
    modes: List[str]
    requires: List[str] = field(default_factory=list)
    name_arg: str = ''
    extra_actions: List[str] = field(default_factory=list)

    @property
    def actions(self) -> List[str]:
        """All ROS actions this task calls (empty for tasks without a package)."""
        return [a for a in [self.action] + self.extra_actions if a]

    @property
    def module(self) -> str:
        return self.class_path.split(':', 1)[0]

    @property
    def class_name(self) -> str:
        return self.class_path.split(':', 1)[1]

    def load_class(self):
        """Import the task class (this imports ROS message modules)."""
        return getattr(importlib.import_module(self.module), self.class_name)


@dataclass
class Catalog:
    tasks: Dict[str, TaskSpec]

    def by_class(self, cls) -> 'TaskSpec | None':
        for spec in self.tasks.values():
            if spec.module == cls.__module__ and spec.class_name == cls.__name__:
                return spec
        return None


class CatalogError(ValueError):
    pass


def _check_spec(name: str, raw: dict) -> TaskSpec:
    for key in ('class', 'args_schema', 'timeout_s', 'modes'):
        if key not in raw:
            raise CatalogError(f"task '{name}': missing '{key}'")
    if raw.get('name_arg') and raw['name_arg'] not in (raw['args_schema'] or {}):
        raise CatalogError(f"task '{name}': name_arg '{raw['name_arg']}' is not an argument")
    if ':' not in raw['class']:
        raise CatalogError(f"task '{name}': class must be 'module:Class'")
    for arg, schema in (raw['args_schema'] or {}).items():
        if not isinstance(schema, dict) or schema.get('type') not in TYPES:
            raise CatalogError(f"task '{name}': argument '{arg}' needs a type out of {TYPES}")
    return TaskSpec(
        name=name,
        class_path=raw['class'],
        action=raw.get('action', ''),
        type=raw.get('type', ''),
        args_schema=dict(raw['args_schema'] or {}),
        timeout_s=float(raw['timeout_s']),
        cancelable=bool(raw.get('cancelable', False)),
        modes=list(raw['modes']),
        requires=list(raw.get('requires') or []),
        name_arg=raw.get('name_arg') or '',
        extra_actions=list(raw.get('extra_actions') or []),
    )


def load_catalog(path: str = DEFAULT_PATH) -> Catalog:
    with open(path, 'r', encoding='utf-8') as f:
        raw = yaml.safe_load(f) or {}
    tasks = raw.get('tasks') or {}
    if not tasks:
        raise CatalogError(f'{path}: no tasks')
    return Catalog({name: _check_spec(name, spec) for name, spec in tasks.items()})
