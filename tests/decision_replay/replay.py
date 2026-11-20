"""Decision replay (plan P5): run a recorded Burr mission again and compare every decision.

A recorded run (Burr tracking: ~/.burr/georg_task_manager/<app_id>/) contains every step
with its state. The replay rebuilds the same mission (mission id = partition key), feeds
the recorded task results back in (``last_result`` of every task step) and runs the
decision logic again, N times. It compares:

- the sequence of Burr steps (e.g. listen_doorbell -> listen_doorbell -> gesture_look_at ...)
- the decision of every task step (``decision`` in the state)
- the final outcome

Any difference is a deviation; the command line exits with 1 and the pytest wrapper fails.
From P6 on, the decision step of the LLM planner is replayed the same way (same inputs,
temperature 0, fixed model and prompt version) and compared as structured task sequence.

    python tests/decision_replay/replay.py <app_id> [--storage ~/.burr] [--runs 3]
"""

import argparse
import asyncio
from dataclasses import dataclass, field
import json
import os
import sys
from typing import List

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, '..', '..'))
TM = os.path.join(REPO, 'packages', 'pkg_task_manager', 'georg_task_manager')
PROJECT = 'georg_task_manager'


def _import_task_manager():
    """Make georg_task_manager importable; stand-ins for ROS modules if ROS is missing."""
    for path in (TM, os.path.join(TM, 'test')):
        if path not in sys.path:
            sys.path.insert(0, path)
    import conftest  # noqa: F401  (installs ROS stand-ins only where needed)


@dataclass
class Recording:
    app_id: str
    mission_id: str
    steps: List[str] = field(default_factory=list)          # Burr actions in order
    decisions: List[str] = field(default_factory=list)      # per task step
    results: List[bool] = field(default_factory=list)       # task results in order
    outcome: str = ''


def load_recording(app_dir: str) -> Recording:
    """Read a Burr tracking directory (log.jsonl + metadata.json)."""
    with open(os.path.join(app_dir, 'metadata.json'), encoding='utf-8') as f:
        meta = json.load(f)
    rec = Recording(app_id=os.path.basename(app_dir.rstrip('/')),
                    mission_id=meta.get('partition_key') or '')
    with open(os.path.join(app_dir, 'log.jsonl'), encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line)
            if entry.get('type') != 'end_entry':
                continue
            rec.steps.append(entry['action'])
            state = entry.get('state') or {}
            if entry['action'] not in ('start_mission', 'finish', 'idle') \
                    and state.get('last_result') is not None:
                rec.results.append(bool(state['last_result']))
                rec.decisions.append(state.get('decision', ''))
            if state.get('outcome'):
                rec.outcome = state['outcome']
    return rec


def replay_once(rec: Recording, tasks) -> Recording:
    """Run the mission again with the recorded task results; record what happened."""
    from georg_task_manager.burr_app.service import TaskManagerService

    results = list(rec.results)
    seen = Recording(app_id='replay', mission_id=rec.mission_id)

    async def recorded_result(task):
        if not results:
            raise RuntimeError('replay asked for more task results than were recorded')
        return results.pop(0)

    def on_step(action, state):
        seen.steps.append(action)
        if action not in ('start_mission', 'finish', 'idle') \
                and state.get('last_result') is not None:
            seen.decisions.append(state.get('decision', ''))

    service = TaskManagerService(run_task=recorded_result, on_step=on_step, tracker=None,
                                 log=lambda line: None)
    result = asyncio.run(service.run_mission(rec.mission_id, tasks))
    if not result.accepted:
        raise RuntimeError(f'replay rejected: {result.reason}')
    seen.outcome = result.outcome
    return seen


def compare(recorded: Recording, replayed: Recording) -> List[str]:
    """List the deviations between a recorded and a replayed run (empty = identical)."""
    out = []
    if recorded.steps != replayed.steps:
        for i, (a, b) in enumerate(zip(recorded.steps, replayed.steps)):
            if a != b:
                out.append(f'step {i}: recorded {a!r}, replay {b!r}')
                break
        if len(recorded.steps) != len(replayed.steps):
            out.append(f'step count: recorded {len(recorded.steps)}, '
                       f'replay {len(replayed.steps)}')
    for i, (a, b) in enumerate(zip(recorded.decisions, replayed.decisions)):
        if a != b:
            out.append(f'decision {i}: recorded {a!r}, replay {b!r}')
    if recorded.outcome and recorded.outcome != replayed.outcome:
        out.append(f'outcome: recorded {recorded.outcome!r}, replay {replayed.outcome!r}')
    return out


def replay(app_dir: str, runs: int = 3, mission_factory=None) -> List[str]:
    """Replay a recorded run ``runs`` times; return all deviations."""
    _import_task_manager()
    from georg_task_manager.mission_selector import get_mission

    rec = load_recording(app_dir)
    factory = mission_factory or get_mission
    deviations = []
    for run in range(runs):
        tasks = factory(rec.mission_id)
        if tasks is None:
            return [f'unknown mission {rec.mission_id!r}']
        deviations += [f'run {run + 1}: {d}' for d in compare(rec, replay_once(rec, tasks))]
    return deviations


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('app_id', help='Burr app id (burr_app_id in /task_manager/status)')
    parser.add_argument('--storage', default=os.environ.get('GEORG_BURR_STORAGE_DIR', '~/.burr'))
    parser.add_argument('--runs', type=int, default=3)
    args = parser.parse_args(argv)
    app_dir = os.path.join(os.path.expanduser(args.storage), PROJECT, args.app_id)
    deviations = replay(app_dir, args.runs)
    if deviations:
        print('\n'.join(deviations))
        return 1
    print(f'{args.app_id}: {args.runs} replays, no deviations')
    return 0


if __name__ == '__main__':
    sys.exit(main())
