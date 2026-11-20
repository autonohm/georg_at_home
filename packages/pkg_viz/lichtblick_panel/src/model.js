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

// link to the run in the Burr UI
function burrUrl(baseUrl, missionId, appId) {
  if (!appId) {
    return "";
  }
  const base = String(baseUrl || "http://localhost:7241").replace(/\/+$/, "");
  return `${base}/project/georg_task_manager/${encodeURIComponent(missionId || "null")}/${encodeURIComponent(appId)}`;
}

module.exports = {
  STATE_NAMES,
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
