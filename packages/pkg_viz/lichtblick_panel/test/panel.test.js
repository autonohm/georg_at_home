// Runs the bundled panel (dist/extension.js) against a fake DOM and a fake Lichtblick context.
// python3 build.py && node --test test/panel.test.js
const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");

class FakeNode {
  constructor(tag) {
    this.tagName = tag;
    this.children = [];
    this.attrs = {};
    this.textContent = "";
    this.className = "";
    this.disabled = false;
    this.value = "";
  }
  setAttribute(k, v) { this.attrs[k] = v; if (k === "class") this.className = v; if (k === "value") this.value = v; }
  removeAttribute(k) { delete this.attrs[k]; }
  appendChild(c) { this.children.push(c); return c; }
  replaceChildren(...cs) {
    this.children = cs;
    if (this.tagName === "select") this.value = cs.length ? cs[0].value : "";
  }
  find(pred) {
    if (pred(this)) return this;
    for (const c of this.children) { const r = c.find(pred); if (r) return r; }
    return undefined;
  }
}

function loadPanel() {
  global.document = { createElement: (tag) => new FakeNode(tag) };
  const code = fs.readFileSync(path.join(__dirname, "..", "dist", "extension.js"), "utf8");
  const module = { exports: {} };
  new Function("module", "exports", code)(module, module.exports);
  let registered;
  module.exports.activate({ registerPanel: (p) => { registered = p; } });
  return registered;
}

function fakeContext() {
  const calls = [];
  const ctx = {
    panelElement: new FakeNode("div"),
    initialState: undefined,
    calls,
    subscribed: [],
    saveState() {},
    updatePanelSettingsEditor() {},
    watch() {},
    subscribe(s) { this.subscribed = s; },
    async callService(name, req) {
      calls.push([name, req]);
      if (name.endsWith("list_missions")) {
        return { mission_ids: ["mock_test", "sim_seat"], display_names: ["Mock Test", "Seat"] };
      }
      if (name.endsWith("start")) return { accepted: true, reason: "", burr_app_id: "run-1" };
      return { accepted: true, reason: "" };
    },
  };
  return ctx;
}

const tick = () => new Promise((r) => setImmediate(r));

test("panel registers, lists missions, starts, shows status and aborts", async () => {
  const panel = loadPanel();
  assert.equal(panel.name, "Georg Task Manager");
  const ctx = fakeContext();
  panel.initPanel(ctx);
  await tick();

  assert.deepEqual(ctx.subscribed, [{ topic: "/task_manager/status" }, { topic: "/task_manager/plan" }]);
  assert.deepEqual(ctx.calls[0], ["/task_manager/list_missions", {}]);
  const select = ctx.panelElement.find((n) => n.tagName === "select");
  assert.equal(select.children.length, 2);
  assert.equal(select.value, "mock_test");

  const button = (label) => ctx.panelElement.find((n) => n.tagName === "button" && n.textContent === label);
  const abort = button("Abort");
  assert.equal(abort.disabled, true); // nothing running yet

  await button("Start").onclick();
  assert.deepEqual(ctx.calls[1], ["/task_manager/start", { mission_id: "mock_test", params_json: "" }]);
  const feedback = ctx.panelElement.find((n) => n.attrs.class === "gtm-feedback");
  assert.match(feedback.textContent, /start: accepted \(run-1\)/);

  let done = false;
  ctx.onRender({ currentFrame: [{ topic: "/task_manager/status", message: {
    state: 1, mission_id: "mock_test", current_task: "Gesture", step: 2, total_steps: 4,
    message: "", burr_app_id: "run-1" } }] }, () => { done = true; });
  assert.equal(done, true);
  const state = ctx.panelElement.find((n) => (n.attrs.class || "").startsWith("gtm-state"));
  assert.equal(state.textContent, "RUNNING");
  assert.equal(abort.disabled, false);
  const link = ctx.panelElement.find((n) => n.tagName === "a");
  assert.equal(link.attrs.href, "http://localhost:7241/project/task_manager/mock_test/run-1");

  await abort.onclick();
  assert.deepEqual(ctx.calls[2], ["/task_manager/cancel", { mission_id: "" }]);
});

test("panel says so when the data source has no services", async () => {
  const panel = loadPanel();
  const ctx = fakeContext();
  delete ctx.callService;
  panel.initPanel(ctx);
  await tick();
  const feedback = ctx.panelElement.find((n) => n.attrs.class === "gtm-feedback");
  assert.match(feedback.textContent, /does not support services/);
});


test("LLM controls: mode, instruction, approval and plan display", async () => {
  const panel = loadPanel();
  const ctx = fakeContext();
  panel.initPanel(ctx);
  await tick();
  const button = (label) => ctx.panelElement.find((n) => n.tagName === "button" && n.textContent === label);
  const selects = [];
  ctx.panelElement.find((n) => { if (n.tagName === "select") selects.push(n); return false; });
  const modeSelect = selects[1];
  modeSelect.value = "llm_approval";
  await button("Set mode").onclick();
  assert.deepEqual(ctx.calls.at(-1), ["/task_manager/set_mode", { mode: "llm_approval" }]);

  ctx.onRender({ currentFrame: [{ topic: "/task_manager/plan", message: { data: JSON.stringify({
    mode: "llm_approval", goal: "greet", waiting_for_approval: true, remaining: ["block greet_guest"],
    reason: "guest is here", history: [{ step: "listen(sound=DOORBELL)", result: "ok" }] }) } }] }, () => {});
  const approve = button("Approve plan");
  assert.equal(approve.disabled, false);
  const plan = ctx.panelElement.find((n) => (n.textContent || "").startsWith("goal: greet"));
  assert.match(plan.textContent, /next: block greet_guest/);
  assert.match(plan.textContent, /✓ listen\(sound=DOORBELL\)/);
  await approve.onclick();
  assert.deepEqual(ctx.calls.at(-1), ["/task_manager/approve_plan", { approve: true }]);

  const input = ctx.panelElement.find((n) => n.tagName === "input");
  input.value = "  bring them to the seat ";
  await button("Send").onclick();
  assert.deepEqual(ctx.calls.at(-1), ["/task_manager/instruct", { text: "bring them to the seat" }]);
  assert.equal(input.value, "");

  ctx.onRender({ currentFrame: [{ topic: "/task_manager/plan", message: { data: '{"mode": "mission"}' } }] }, () => {});
  assert.equal(button("Send").disabled, true);
  assert.equal(button("Approve plan").disabled, true);
});
