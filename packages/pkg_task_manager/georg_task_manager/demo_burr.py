"""Burr demo without robot and without ROS.

Runs the Digital Festival mission with fake tasks (each takes ~1 s) and records
every run for the Burr UI. Three runs: everything works, one task fails, abort.

    pip install "apache-burr[tracking]==0.43.0" pyyaml
    python demo_burr.py                # write runs to ~/.burr
    burr_path=~/.burr python -m uvicorn burr.tracking.server.run:app --port 7241
    # open http://localhost:7241 -> project georg_task_manager
"""

import argparse
import asyncio
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "test"))
import conftest  # noqa: E402,F401  (ROS stand-ins if ROS is not installed)

from georg_task_manager.burr_app.builder import make_tracker  # noqa: E402
from georg_task_manager.burr_app.service import TaskManagerService  # noqa: E402
from georg_task_manager.missions import DigitalFestival  # noqa: E402


async def demo(delay: float):
    service = None
    scenario = {"fail": None, "abort_at": None}
    count = {"n": 0}

    async def fake_run(task):
        count["n"] += 1
        print(f"    ... {task.name} läuft")
        await asyncio.sleep(delay)
        if scenario["abort_at"] == count["n"]:
            print("    !!! Abbruch durch Bedienperson")
            service.request_abort()
            return False
        if scenario["fail"] == task.name:
            return False
        return True

    service = TaskManagerService(run_task=fake_run, tracker=make_tracker())

    runs = [
        ("1 alles klappt", {"fail": None, "abort_at": None}),
        ("2 Klingel wird nie erkannt (HIGH: 3 Wiederholungen)",
         {"fail": "Listening(DOORBELL)", "abort_at": None}),
        ("3 Abbruch während des dritten Tasks", {"fail": None, "abort_at": 3}),
    ]
    for title, sc in runs:
        scenario.update(sc)
        count["n"] = 0
        print(f"\n### Lauf {title}")
        result = await service.run_mission("digital_festival", DigitalFestival.get_mission())
        print(f"### Ergebnis: {result.outcome}  burr_app_id={result.burr_app_id}")
        print(f"### Burr-Schritte: {' -> '.join(result.steps)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--delay", type=float, default=1.0, help="Sekunden pro Task")
    asyncio.run(demo(parser.parse_args().delay))
