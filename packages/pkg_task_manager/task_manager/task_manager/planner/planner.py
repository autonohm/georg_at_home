"""LLM planner with automatic guard rails (plan P6, "Ablauf einer LLM-Entscheidung").

1. The caller builds a compact context (goal, operator feedback, robot state, history of
   task results, remaining plan, available tasks and blocks, known places).
2. The LLM answers with JSON: decision + steps (tasks and blocks) + reason.
3. The answer is checked automatically: JSON form, decision value, catalog entries,
   arguments, mode, preconditions, maximum chain length. An invalid answer goes back to
   the LLM with the error text; after ``max_attempts`` the planner gives up (-> Idle).
4. Every decision is logged (prompt version, model, input, raw answers, plan, result)
   and can be replayed (tests/decision_replay).
"""

from dataclasses import asdict, dataclass, field
import datetime
import json
import os
from typing import Callable, List, Optional

from georg_task_manager.catalog import Catalog
from georg_task_manager.catalog.validator import validate_plan
from georg_task_manager.planner import prompts

DECISIONS = ('plan', 'continue', 'done', 'abort')
DEFAULT_MAX_STEPS = 8
DEFAULT_MAX_ATTEMPTS = 3


@dataclass
class PlannerDecision:
    decision: str                 # plan | continue | done | abort | invalid
    items: List[dict] = field(default_factory=list)   # validated steps (plan only)
    reason: str = ''
    record: dict = field(default_factory=dict)        # what was logged

    @property
    def valid(self) -> bool:
        return self.decision != 'invalid'


def _parse(raw: str):
    text = raw.strip()
    if text.startswith('```'):
        text = text.strip('`')
        text = text[text.find('{'):] if '{' in text else text
    start, end = text.find('{'), text.rfind('}')
    if start < 0 or end < start:
        raise ValueError('answer contains no JSON object')
    return json.loads(text[start:end + 1])


class Planner:

    def __init__(self, chat: Callable[[List[dict]], str], catalog: Catalog, mode: str,
                 model: str = 'unknown', max_steps: int = DEFAULT_MAX_STEPS,
                 max_attempts: int = DEFAULT_MAX_ATTEMPTS, log_dir: Optional[str] = None,
                 constrained: bool = True):
        self.chat = chat
        self.catalog = catalog
        self.mode = mode
        self.model = model
        self.max_steps = max_steps
        self.max_attempts = max_attempts
        # send the answer schema to the LLM server (constrained decoding)
        self.constrained = constrained
        self.log_dir = log_dir if log_dir is not None else os.path.expanduser(
            os.environ.get('GEORG_DECISION_LOG_DIR', '~/.georg/decisions'))

    def context(self, goal: str, history: List[dict], remaining: List[dict],
                feedback: str = '', robot: Optional[dict] = None,
                places: Optional[List[str]] = None) -> dict:
        """Compact input of one decision; also what the decision replay feeds in again."""
        return {
            'goal': goal,
            'operator_feedback': feedback,
            'robot': robot or {},
            'history': history[-10:],
            'remaining_plan': remaining,
            'plan_finished': bool(history) and not remaining,
            'available': prompts.available(self.catalog, self.mode),
            'places': places or [],
            'limits': {'max_steps': self.max_steps},
        }

    def check(self, answer, context: Optional[dict] = None) -> List[str]:
        """Errors of a parsed answer (empty = valid)."""
        if not isinstance(answer, dict):
            return ['answer must be a JSON object']
        decision = answer.get('decision')
        if decision not in DECISIONS:
            return [f'decision must be one of {list(DECISIONS)}, got {decision!r}']
        steps = answer.get('steps', [])
        context = context or {}
        if decision != 'plan':
            if steps:
                return [f"decision '{decision}' takes no steps"]
            if decision == 'continue' and not context.get('remaining_plan'):
                return ["nothing to continue: no remaining plan; answer 'plan', 'done' or "
                        "'abort'"]
            return []
        result = validate_plan(steps, self.catalog, self.mode, max_steps=self.max_steps)
        errors = list(result.errors)
        places = context.get('places') or []
        if places and not errors:
            for i, step in enumerate(steps):
                for arg in prompts.PLACE_ARGS:
                    value = (step.get('args') or {}).get(arg)
                    if value is not None and value not in places:
                        errors.append(f"step {i}: unknown place '{value}' (places: {places})")
        return errors

    def decide(self, context: dict) -> PlannerDecision:
        messages = [{'role': 'system',
                     'content': prompts.system_prompt(self.max_steps, self.catalog, self.mode)},
                    {'role': 'user', 'content': prompts.user_message(context)}]
        record = {
            'time': datetime.datetime.now().isoformat(timespec='seconds'),
            'prompt_version': prompts.PROMPT_VERSION,
            'model': self.model,
            'mode': self.mode,
            'input': context,
            'attempts': [],
        }
        for _ in range(self.max_attempts):
            if self.constrained:
                schema = prompts.answer_schema(self.catalog, self.mode, self.max_steps,
                                               context.get('places'))
                raw = self.chat(messages, schema=schema)
            else:
                raw = self.chat(messages)
            try:
                answer = _parse(raw)
                errors = self.check(answer, context)
            except ValueError as exc:
                answer, errors = None, [f'invalid JSON: {exc}']
            record['attempts'].append({'raw': raw, 'errors': errors})
            if not errors:
                items = (validate_plan(answer['steps'], self.catalog, self.mode,
                                       max_steps=self.max_steps).items
                         if answer['decision'] == 'plan' else [])
                result = PlannerDecision(answer['decision'], items,
                                         str(answer.get('reason', ''))[:300])
                return self._log(result, record)
            messages += [{'role': 'assistant', 'content': raw},
                         {'role': 'user', 'content': 'Your answer was rejected: '
                          + '; '.join(errors) + '. Answer again with one valid JSON object.'}]
        last = record['attempts'][-1]['errors']
        return self._log(PlannerDecision(
            'invalid', [], f'no valid plan after {self.max_attempts} attempts: '
            + '; '.join(last)), record)

    def _log(self, result: PlannerDecision, record: dict) -> PlannerDecision:
        record.update(decision=result.decision, steps=result.items, reason=result.reason)
        result.record = record
        if self.log_dir:
            os.makedirs(self.log_dir, exist_ok=True)
            path = os.path.join(self.log_dir, datetime.date.today().isoformat() + '.jsonl')
            with open(path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
        return result


def as_dict(decision: PlannerDecision) -> dict:
    return asdict(decision)
