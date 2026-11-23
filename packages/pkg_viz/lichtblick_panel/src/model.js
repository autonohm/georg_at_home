// Pure logic of the task manager panel (no DOM, no Lichtblick): testable with `node --test`.
// Interfaces: packages/pkg_interfaces/georg_task_manager_msgs

const STATE_NAMES = ["IDLE", "RUNNING", "SUCCEEDED", "FAILED", "ABORTED"];
const FINAL_STATES = new Set(["SUCCEEDED", "FAILED", "ABORTED"]);

function serviceNames(namespace) {
  const ns = normalizeNamespace(namespace);
  return {
    start: `${ns}/task_manager/start`,
    cancel: `${ns}/task_manager/cancel`,
    list: `${ns}/task_manager/list_missions`,
    status: `${ns}/task_manager/status`,
    setMode: `${ns}/task_manager/set_mode`,
    instruct: `${ns}/task_manager/instruct`,
    approve: `${ns}/task_manager/approve_plan`,
    plan: `${ns}/task_manager/plan`,
  };
}

function normalizeNamespace(namespace) {
  const ns = String(namespace ?? "").trim().replace(/\/+$/, "");
  if (ns === "") {
    return "";
  }
  return ns.startsWith("/") ? ns : `/${ns}`;
}

function stateName(state) {
  return STATE_NAMES[Number(state)] ?? `UNKNOWN(${state})`;
}

// MissionStatus message -> what the panel shows
function describeStatus(msg) {
  if (msg == undefined) {
    return { state: "NO STATUS", running: false, final: false, lines: ["waiting for /task_manager/status"] };
  }
  const state = stateName(msg.state);
  const lines = [];
  if (msg.mission_id) {
    lines.push(`mission: ${msg.mission_id}`);
  }
  if (msg.current_task) {
    lines.push(`task: ${msg.current_task}`);
  }
  if (msg.total_steps > 0) {
    lines.push(`step: ${msg.step} / ${msg.total_steps}`);
  }
  if (msg.message) {
    lines.push(`message: ${msg.message}`);
  }
  if (msg.burr_app_id) {
    lines.push(`burr_app_id: ${msg.burr_app_id}`);
  }
  return { state, running: state === "RUNNING", final: FINAL_STATES.has(state), lines };
}

// ListMissions response -> dropdown entries
function missionOptions(response) {
  const ids = response?.mission_ids ?? [];
  const names = response?.display_names ?? [];
  return ids.map((id, i) => ({ id, label: names[i] ? `${names[i]} (${id})` : id }));
}

function startRequest(missionId, paramsJson) {
  return { mission_id: String(missionId ?? ""), params_json: String(paramsJson ?? "") };
}

function cancelRequest(missionId) {
  return { mission_id: String(missionId ?? "") };
}

// StartMission / CancelMission response -> one line of feedback
function describeResponse(kind, response) {
  if (response == undefined) {
    return `${kind}: no response`;
  }
  if (response.accepted) {
    return response.burr_app_id ? `${kind}: accepted (${response.burr_app_id})` : `${kind}: accepted`;
  }
  return `${kind}: rejected – ${response.reason || "no reason given"}`;
}

const MODES = ["mission", "llm", "llm_approval"];
const MODE_LABELS = { mission: "Mission", llm: "LLM", llm_approval: "LLM + approval" };

// std_msgs/String with JSON on <ns>/task_manager/plan -> what the panel shows
function describePlan(msg) {
  let plan = {};
  try {
    plan = JSON.parse(msg?.data ?? "{}");
  } catch {
    return { mode: "", waiting: false, lines: ["plan: unreadable"] };
  }
  const lines = [];
  if (plan.goal) lines.push(`goal: ${plan.goal}`);
  if (plan.current) lines.push(`now: ${plan.current}`);
  if (plan.remaining?.length) lines.push(`next: ${plan.remaining.join(" → ")}`);
  if (plan.reason) lines.push(`LLM: ${plan.reason}`);
  if (plan.outcome) lines.push(`result: ${plan.outcome}`);
  for (const h of (plan.history ?? []).slice(-5)) {
    lines.push(`  ${h.result === "ok" ? "✓" : "✗"} ${h.step}`);
  }
  return { mode: plan.mode ?? "", waiting: Boolean(plan.waiting_for_approval), lines };
}

function setModeRequest(mode) {
  return { mode: String(mode ?? "") };
}

function instructRequest(text) {
  return { text: String(text ?? "").trim() };
}

function approveRequest(ok) {
  return { approve: Boolean(ok) };
}

// link to the run in the Burr UI
function burrUrl(baseUrl, missionId, appId) {
  if (!appId) {
    return "";
  }
  const base = String(baseUrl || "http://localhost:7241").replace(/\/+$/, "");
  return `${base}/project/task_manager/${encodeURIComponent(missionId || "null")}/${encodeURIComponent(appId)}`;
}

// world switch of the simulator (pkg_sim georg_sim/worlds.py); topics are not namespaced
const WORLD_TOPICS = { current: "/sim/world", list: "/sim/worlds", set: "/sim/set_world" };

// std_msgs/String with a JSON list of map files -> dropdown options
function worldOptions(msg) {
  let names = [];
  try {
    names = JSON.parse(msg?.data ?? "[]");
  } catch (err) {
    names = [];
  }
  if (!Array.isArray(names)) {
    return [];
  }
  return names.map((n) => ({ id: String(n), label: String(n).replace(/\.yaml$/, "") }));
}

module.exports = {
  WORLD_TOPICS,
  worldOptions,
  STATE_NAMES,
  MODES,
  MODE_LABELS,
  describePlan,
  setModeRequest,
  instructRequest,
  approveRequest,
  serviceNames,
  normalizeNamespace,
  stateName,
  describeStatus,
  missionOptions,
  startRequest,
  cancelRequest,
  describeResponse,
  burrUrl,
};
