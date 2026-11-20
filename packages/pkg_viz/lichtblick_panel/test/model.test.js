// node --test test/
const test = require("node:test");
const assert = require("node:assert/strict");
const m = require("../src/model.js");

test("service names follow the robot namespace", () => {
  assert.deepEqual(m.serviceNames("georg"), {
    start: "/georg/task_manager/start",
    cancel: "/georg/task_manager/cancel",
    list: "/georg/task_manager/list_missions",
    status: "/georg/task_manager/status",
  });
  assert.equal(m.serviceNames("/georg/").start, "/georg/task_manager/start");
  assert.equal(m.serviceNames("").start, "/task_manager/start");
});

test("status is described with state, task, step and burr id", () => {
  const d = m.describeStatus({
    state: 1, mission_id: "mock_test", current_task: "Gesture", step: 2, total_steps: 4,
    message: "ok | -> gesture_look_at", burr_app_id: "abc",
  });
  assert.equal(d.state, "RUNNING");
  assert.equal(d.running, true);
  assert.equal(d.final, false);
  assert.deepEqual(d.lines, [
    "mission: mock_test", "task: Gesture", "step: 2 / 4",
    "message: ok | -> gesture_look_at", "burr_app_id: abc",
  ]);
  assert.equal(m.describeStatus({ state: 4 }).final, true);
  assert.equal(m.describeStatus(undefined).state, "NO STATUS");
  assert.equal(m.stateName(9), "UNKNOWN(9)");
});

test("mission list becomes dropdown entries", () => {
  assert.deepEqual(
    m.missionOptions({ mission_ids: ["a", "b"], display_names: ["Alpha", ""] }),
    [{ id: "a", label: "Alpha (a)" }, { id: "b", label: "b" }],
  );
  assert.deepEqual(m.missionOptions(undefined), []);
});

test("requests match the service definitions", () => {
  assert.deepEqual(m.startRequest("mock_test"), { mission_id: "mock_test", params_json: "" });
  assert.deepEqual(m.cancelRequest(), { mission_id: "" });
});

test("responses become one line of feedback", () => {
  assert.equal(m.describeResponse("start", { accepted: true, burr_app_id: "x" }), "start: accepted (x)");
  assert.equal(
    m.describeResponse("start", { accepted: false, reason: "action server not reachable: nav/drive_route" }),
    "start: rejected – action server not reachable: nav/drive_route",
  );
  assert.equal(m.describeResponse("cancel", undefined), "cancel: no response");
});

test("burr link points at the run", () => {
  assert.equal(m.burrUrl("", "mock_test", "id1"),
    "http://localhost:7241/project/georg_task_manager/mock_test/id1");
  assert.equal(m.burrUrl("http://x:1/", "", "id1"), "http://x:1/project/georg_task_manager/null/id1");
  assert.equal(m.burrUrl("", "m", ""), "");
});
