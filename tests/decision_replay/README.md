# Decision replay

Runs a recorded mission again and compares every decision (plan P5).

A run is identified by its `burr_app_id` (in `/georg/task_manager/status`, in the Burr UI and
in the continuous MCAP recording). The replay rebuilds the mission, feeds the recorded task
results back in and runs the decision logic N times. Every difference in the Burr steps, the
decisions or the outcome is a deviation: the command exits with 1, the tests fail.

```bash
python tests/decision_replay/replay.py <burr_app_id> --runs 3 [--storage ~/.burr]
pixi run replay <burr_app_id>            # on a Mac, from dev/macos
python -m pytest tests/decision_replay   # the replay itself is tested here
```

Use it after every change to the task manager rules, and from P6 on after every change of
prompt or model: same inputs, temperature 0, fixed model and prompt version, compared as
structured task sequence, not as text.

## MCAP replay

| Step | How |
| --- | --- |
| record `/georg/task_manager/*` all the time | compose service `recorder` (every profile), `pixi run record` |
| strip a recording to raw sensors | `packages/pkg_slam/tools/mcap_raw_only.py <in> <out>` (drops `/map`, `map -> odom`, task manager topics) |
| replay with live SLAM and Burr | `GEORG_MCAP_FILE=<bag> ./projectctl.bash up mcap` (the player strips automatically) |

Rules (plan): open loop, recorded odometry does not react to commands; only raw sensors;
`/clock` from the player and `use_sim_time` for SLAM; one source per topic
(in `mcap` the mocks publish no `odom`).
Tested in `packages/pkg_task_manager/task_manager_pkg/test/test_mcap_integration.py`
(`pixi run test_mcap`).
