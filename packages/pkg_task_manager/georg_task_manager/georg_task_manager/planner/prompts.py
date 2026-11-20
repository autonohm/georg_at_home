"""Prompt of the LLM planner (plan P6). Change PROMPT_VERSION with every change of the text."""

import json

from georg_task_manager.catalog import Catalog

PROMPT_VERSION = 'planner-v3'

SYSTEM = """You are the task planner of Georg, a service robot in a bar.
You do not move the robot yourself. You choose tasks and mission blocks from a catalog;
the task manager checks your answer and executes it step by step.

Answer with ONE JSON object and nothing else:
{"decision": "plan" | "continue" | "done" | "abort",
 "steps": [{"task": "<task name>", "args": {...}} or {"block": "<block name>"}],
 "reason": "<one short sentence>"}

- "plan": replace the remaining plan by "steps" (1 to MAX_STEPS steps).
- "continue": keep the remaining plan (steps: []).
- "done": the goal is reached (steps: []).
- "abort": stop safely, e.g. the goal cannot be reached (steps: []).

Rules:
- Tasks (use as {"task": name, "args": {...}}): TASK_NAMES.
- Blocks (use as {"block": name}): BLOCK_NAMES.
- Use only the listed arguments.
- Prefer blocks: they are tested sequences.
- Navigate only to places listed in "places". Never invent file paths.
- After a failed task you may retry it once, plan something else, or abort.
- "history" lists the steps already executed with their result.
- If "plan_finished" is true, every step of your last plan has been executed:
  answer "done" if the history shows the goal is reached, otherwise plan only the
  missing steps. Never repeat steps that already succeeded.
- When the goal is reached, answer "done".
"""


def system_prompt(max_steps: int, catalog: Catalog = None, mode: str = '') -> str:
    text = SYSTEM.replace('MAX_STEPS', str(max_steps))
    if catalog is not None:
        av = available(catalog, mode)
        text = text.replace('TASK_NAMES', ', '.join(av['tasks']) or '-')
        text = text.replace('BLOCK_NAMES', ', '.join(av['blocks']) or '-')
    return text


_JSON_TYPES = {'string': 'string', 'number': 'number', 'integer': 'integer',
               'boolean': 'boolean'}


PLACE_ARGS = ('object_name', 'room_name')


def answer_schema(catalog: Catalog, mode: str, max_steps: int, places=None) -> dict:
    """JSON schema of a valid answer, built from the catalog.

    Servers with constrained decoding (llama.cpp, vLLM, Ollama) only let the model produce
    answers of this form: only catalog names, only allowed arguments and values.
    The validator still checks every answer (second line of defence).
    """
    steps = []
    for name, spec in catalog.tasks.items():
        if mode and mode not in spec.modes:
            continue
        props, required = {}, []
        for arg, schema in spec.args_schema.items():
            if arg == 'map_path':
                continue
            prop = {'type': _JSON_TYPES[schema['type']]}
            if 'enum' in schema:
                prop['enum'] = list(schema['enum'])
            if arg in PLACE_ARGS and places:
                prop['enum'] = list(places)       # only places of the map
            props[arg] = prop
            if schema.get('required', True):
                required.append(arg)
        steps.append({'type': 'object', 'additionalProperties': False,
                      'required': ['task', 'args'],
                      'properties': {'task': {'const': name},
                                     'args': {'type': 'object', 'additionalProperties': False,
                                              'properties': props, 'required': required}}})
    for name, block in catalog.blocks.items():
        if mode and mode not in block.modes:
            continue
        steps.append({'type': 'object', 'additionalProperties': False, 'required': ['block'],
                      'properties': {'block': {'const': name}}})
    reason = {'type': 'string', 'maxLength': 200}
    return {'oneOf': [
        {'type': 'object', 'additionalProperties': False,
         'required': ['decision', 'steps', 'reason'],
         'properties': {'decision': {'const': 'plan'}, 'reason': reason,
                        'steps': {'type': 'array', 'minItems': 1, 'maxItems': max_steps,
                                  'items': {'anyOf': steps}}}},
        {'type': 'object', 'additionalProperties': False,
         'required': ['decision', 'steps', 'reason'],
         'properties': {'decision': {'enum': ['continue', 'done', 'abort']}, 'reason': reason,
                        'steps': {'type': 'array', 'maxItems': 0}}},
    ]}


def available(catalog: Catalog, mode: str) -> dict:
    """Catalog in the compact form the LLM sees."""
    tasks = {}
    for name, spec in catalog.tasks.items():
        if mode and mode not in spec.modes:
            continue
        args = {}
        for arg, schema in spec.args_schema.items():
            if arg == 'map_path':
                continue                      # the robot's map is used automatically
            text = schema['type']
            if 'enum' in schema:
                text += ' one of ' + '|'.join(str(v) for v in schema['enum'])
            if not schema.get('required', True):
                text += ' (optional)'
            args[arg] = text
        tasks[name] = {'description': spec.description, 'args': args}
    blocks = {name: block.description for name, block in catalog.blocks.items()
              if not mode or mode in block.modes}
    return {'tasks': tasks, 'blocks': blocks}


def user_message(context: dict) -> str:
    """Compact situation for one decision (no raw sensor data)."""
    return json.dumps(context, ensure_ascii=False, sort_keys=True)
