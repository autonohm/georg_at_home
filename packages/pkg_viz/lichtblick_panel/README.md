# Georg Task Manager – Lichtblick panel

Panel for [Lichtblick](https://github.com/lichtblick-suite/lichtblick) (tested with **1.30.0**, pinned):
mission list, start, abort, live status (state, mission, task, step, message), `burr_app_id`
with a link to the run in the Burr UI.

## Install

```bash
python3 build.py                        # -> georg-task-manager-panel-0.1.0.foxe
```

In Lichtblick: *Extensions → Install extension from file* and pick the `.foxe` file.
Then add the panel *Georg Task Manager* to a layout.

## Connect

Data source *Foxglove WebSocket*, `ws://<robot>:8765` (service `foxglove_bridge` in
compose, every profile; on a Mac without Docker:
`ros2 launch foxglove_bridge foxglove_bridge_launch.xml min_qos_depth:=10`).
The panel needs a data source with services; recordings (MCAP) only show the status.

Panel settings: robot namespace (default `/georg`) and Burr UI URL (default `http://localhost:7241`).

## How it works

| Panel | ROS |
| --- | --- |
| mission dropdown | service `<ns>/task_manager/list_missions` |
| Start | service `<ns>/task_manager/start` (`StartMission`) |
| Abort | service `<ns>/task_manager/cancel` (`CancelMission`) |
| status box | topic `<ns>/task_manager/status` (`MissionStatus`), updated on every Burr step |

Plain JavaScript, no npm: `src/model.js` (logic) and `src/extension.js` (DOM) are bundled by
`build.py`. `foxglove_bridge` 3.x only speaks `foxglove.sdk.v1`; Lichtblick 1.30 offers it.

## Tests

```bash
python3 build.py && node --test test/model.test.js test/panel.test.js
```

`panel.test.js` runs the bundled panel against a fake DOM and a fake Lichtblick context.
`pkg_task_manager/georg_task_manager/test/test_lichtblick_bridge.py` operates the task manager
through `foxglove_bridge` with the same WebSocket protocol as Lichtblick (`pixi run test_lichtblick`).
Not tested automatically: the panel inside a running Lichtblick window.
