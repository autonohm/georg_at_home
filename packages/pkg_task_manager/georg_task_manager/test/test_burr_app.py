"""Burr engine: Idle -> Mission -> Idle, success, failure, abort, same order as before.

Runs without ROS and without a robot: tasks are executed by fake runners.
"""

import asyncio
import random
from unittest.mock import MagicMock

import pytest

from georg_task_manager.burr_app.service import IDLE, TaskManagerService
from georg_task_manager.catalog import Catalog, TaskSpec, load_catalog
from georg_task_manager.interface import RobotState
from georg_task_manager.missions import DigitalFestival
from georg_task_manager.task_manager import TaskManager
from georg_task_manager.tasks.base import BaseTask
from georg_task_manager.tasks.priority import CRITICAL, HIGH, LOW, MID


class FakeTask(BaseTask):
    """Task with scripted results; True once the script is used up."""

    def __init__(self, name, priority=LOW, results=(), log=None):
        super().__init__(name, priority)
        self.results = list(results)
        self.log = log if log is not None else []

    async def run(self, robot=None, state=None):
        self.log.append(self.name)
        return self.results.pop(0) if self.results else True


def fake_catalog():
    spec = TaskSpec(name="fake", class_path=f"{FakeTask.__module__}:FakeTask", action="",
                    type="", args_schema={}, timeout_s=1, cancelable=True,
                    modes=["mock"])
    return Catalog({"fake": spec})


def service(run_task=None, catalog=None, tracker=None):
    async def default_run(task):
        return await task.run()
    return TaskManagerService(run_task=run_task or default_run,
                              catalog=catalog or fake_catalog(),
                              tracker=tracker, log=lambda line: None)


def run(svc, tasks, mission_id="test"):
    return asyncio.run(svc.run_mission(mission_id, tasks))


# --- success and failure paths -------------------------------------------------

def test_success_path_ends_in_idle():
    svc = service()
    result = run(svc, [FakeTask("a"), FakeTask("b"), FakeTask("c")])
    assert result.accepted
    assert result.outcome == "succeeded"
    assert result.executed == ["a", "b", "c"]
    assert svc.state == IDLE and not svc.running


def test_low_failure_is_discarded_and_mission_continues():
    result = run(service(), [FakeTask("a", LOW, [False]), FakeTask("b")])
    assert result.outcome == "succeeded"
    assert result.executed == ["a", "b"]


def test_mid_failure_retries_after_next_task():
    result = run(service(), [FakeTask("a", MID, [False]), FakeTask("b"), FakeTask("c")])
    assert result.executed == ["a", "b", "a", "c"]


def test_high_failure_retries_immediately_three_times():
    result = run(service(), [FakeTask("a", HIGH, [False] * 10), FakeTask("b")])
    assert result.executed == ["a"] * 4 + ["b"]
    assert result.outcome == "succeeded"


def test_critical_failure_fails_mission():
    result = run(service(), [FakeTask("a", CRITICAL, [False] * 10), FakeTask("b")])
    assert result.outcome == "failed"
    assert result.executed == ["a"] * 4
    assert "critical" in result.message


def test_crashing_task_counts_as_failure():
    async def crash(task):
        raise RuntimeError("boom")
    result = run(service(run_task=crash), [FakeTask("a", CRITICAL)])
    assert result.outcome == "failed"
    assert result.executed == ["a"] * 4


# --- abort -------------------------------------------------------------------

def test_abort_during_task_stops_before_next_task():
    svc = service()

    async def run_task(task):
        if task.name == "b":
            svc.request_abort()     # operator cancels while b runs
            return False            # the cancelled action reports failure
        return True

    svc._run_task = run_task
    result = run(svc, [FakeTask("a"), FakeTask("b", HIGH), FakeTask("c")])
    assert result.outcome == "aborted"
    assert result.executed == ["a", "b"]
    assert svc.state == IDLE


def test_abort_without_mission_is_refused():
    assert service().request_abort() is False


def test_second_start_while_running_is_rejected():
    gate = None

    async def scenario():
        nonlocal gate
        gate = asyncio.Event()

        async def slow(task):
            await gate.wait()
            return True

        svc = service(run_task=slow)
        first = asyncio.ensure_future(svc.run_mission("one", [FakeTask("a")]))
        await asyncio.sleep(0.05)
        second = await svc.run_mission("two", [FakeTask("b")])
        gate.set()
        return await first, second

    first, second = asyncio.run(scenario())
    assert first.outcome == "succeeded"
    assert not second.accepted and "still running" in second.reason


def test_unknown_task_class_is_rejected():
    class NotInCatalog(BaseTask):
        async def run(self, robot=None, state=None):
            return True
    result = run(service(), [NotInCatalog("x")])
    assert not result.accepted
    assert "not in the catalog" in result.reason


# --- ten missions in a row, no restart ---------------------------------------

def test_ten_missions_in_a_row_without_restart():
    svc = service()
    ids = set()
    for i in range(10):
        result = run(svc, [FakeTask("a"), FakeTask("b", MID, [False])], mission_id=f"m{i}")
        assert result.outcome == "succeeded"
        assert svc.state == IDLE
        ids.add(result.burr_app_id)
    assert len(ids) == 10


# --- same order as the previous task manager ---------------------------------

def _legacy(tasks):
    log = []
    for t in tasks:
        t.log = log
    state = RobotState()
    ok = asyncio.run(TaskManager(None, state, MagicMock()).run(tasks))
    return ok, log


def _scenario(seed):
    rnd = random.Random(seed)
    spec = []
    for i in range(rnd.randint(1, 7)):
        prio = rnd.choice([LOW, MID, HIGH, CRITICAL])
        results = [rnd.random() < 0.6 for _ in range(rnd.randint(0, 5))]
        spec.append((f"t{i}", prio, results))
    return spec


@pytest.mark.parametrize("seed", range(60))
def test_same_order_and_outcome_as_previous_task_manager(seed):
    spec = _scenario(seed)
    legacy_ok, legacy_log = _legacy([FakeTask(n, p, r) for n, p, r in spec])
    result = run(service(), [FakeTask(n, p, r) for n, p, r in spec])
    assert result.executed == legacy_log
    assert (result.outcome == "succeeded") == legacy_ok


def test_digital_festival_runs_in_mission_order():
    mission = DigitalFestival.get_mission()
    seen = []

    async def ok(task):
        seen.append(task.name)
        return True

    svc = service(run_task=ok, catalog=load_catalog())
    result = run(svc, mission, mission_id="digital_festival")
    assert result.outcome == "succeeded"
    assert result.executed == [t.name for t in mission] == seen
    assert result.executed == ["Listening(DOORBELL)", "Gesture", "Gesture",
                               "Listening(SPEECH)", "Gesture", "Gesture", "ReturnToIdle"]


# --- Burr UI ------------------------------------------------------------------

def test_each_run_is_tracked_for_the_burr_ui(tmp_path, monkeypatch):
    monkeypatch.setenv("GEORG_BURR_TRACKING", "1")
    from georg_task_manager.burr_app.builder import PROJECT, make_tracker

    tracker = make_tracker(storage_dir=str(tmp_path))
    svc = service(tracker=tracker)
    a = run(svc, [FakeTask("a")], mission_id="one")
    b = run(svc, [FakeTask("b")], mission_id="two")
    project_dir = tmp_path / PROJECT
    runs = {p.name for p in project_dir.iterdir()}
    assert a.burr_app_id in runs and b.burr_app_id in runs
    log = (project_dir / a.burr_app_id / "log.jsonl").read_text()
    assert "start_mission" in log and "idle" in log


# --- one Burr node per mission step: the UI shows the sequence at a glance ---

def _festival_service(results):
    """Digital Festival with scripted results per task name (True when used up)."""
    results = {k: list(v) for k, v in results.items()}

    async def scripted(task):
        queue = results.get(task.name, [])
        return queue.pop(0) if queue else True

    return service(run_task=scripted, catalog=load_catalog())


def test_burr_steps_show_each_mission_step_as_its_own_node():
    result = run(_festival_service({}), DigitalFestival.get_mission(), "digital_festival")
    assert result.steps == [
        "start_mission",
        "listen_doorbell", "gesture_look_at", "gesture_point_to", "listen_speech",
        "gesture_look_at_2", "gesture_greet_person", "return_to_idle",
        "finish", "idle",
    ]


def test_retry_shows_up_as_repeated_task_node():
    svc = _festival_service({"Listening(DOORBELL)": [False, True]})
    result = run(svc, DigitalFestival.get_mission(), "digital_festival")
    assert result.steps[:4] == ["start_mission", "listen_doorbell", "listen_doorbell",
                                "gesture_look_at"]
    assert result.outcome == "succeeded"


def test_graph_is_a_line_with_only_the_needed_extra_arrows():
    from georg_task_manager.burr_app.builder import possible_edges

    # LOW, HIGH, MID, CRITICAL
    edges = possible_edges([LOW, HIGH, MID, CRITICAL])
    start, finish = -1, -2
    assert (start, 0) in edges                      # start -> 1
    assert {(0, 1), (1, 2), (2, 3)} <= edges        # straight line
    assert (1, 1) in edges and (3, 3) in edges      # HIGH / CRITICAL retry
    assert (0, 0) not in edges and (2, 2) not in edges   # LOW / MID never retry in place
    assert (3, 2) in edges                          # MID retry after the next task
    assert all((i, finish) in edges for i in range(4))   # abort is possible everywhere
    # nothing jumps across the mission
    assert not any(dst >= 0 and src >= 0 and abs(dst - src) > 2 for src, dst in edges)


def test_mid_retry_runs_back_one_step():
    tasks = [FakeTask("a", MID, [False]), FakeTask("b"), FakeTask("c")]
    result = run(service(), tasks)
    assert result.steps[1:5] == ["fake", "fake_2", "fake", "fake_3"]


def test_node_names_are_readable_and_unique():
    from georg_task_manager.burr_app.actions import make_node_names

    class T:
        def __init__(self, **kw):
            self.__dict__.update(kw)

    tasks = [T(mode="look_at"), T(mode="look_at"), T(sound="DOORBELL"), T(mode="Point To!"),
             T(), T(object_name="")]
    types = ["gesture", "gesture", "listen", "gesture", "finish", "navigate_object"]
    names = make_node_names(tasks, types, {"gesture": "mode", "listen": "sound",
                                           "navigate_object": "object_name"})
    assert names == ["gesture_look_at", "gesture_look_at_2", "listen_doorbell",
                     "gesture_point_to", "finish_2", "navigate_object"]
