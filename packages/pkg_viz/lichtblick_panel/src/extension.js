// Lichtblick panel "Georg Task Manager" (plan P4): mission list, start, abort, live status.
// Plain JavaScript without build tools; build.py bundles it with model.js into a .foxe file.
// Needs a data source that supports services (foxglove_bridge on the robot / in compose).

/* global model */

const CSS = `
.gtm { font: 13px system-ui, sans-serif; padding: 8px; display: flex; flex-direction: column; gap: 8px; height: 100%; box-sizing: border-box; overflow: auto; }
.gtm-row { display: flex; gap: 6px; align-items: center; flex-wrap: wrap; }
.gtm select, .gtm input { flex: 1; min-width: 120px; padding: 4px; }
.gtm button { padding: 4px 10px; cursor: pointer; }
.gtm-state { font-weight: 600; font-size: 15px; padding: 4px 8px; border-radius: 4px; display: inline-block; }
.gtm-IDLE { background: #8884; } .gtm-RUNNING { background: #2a7fff44; }
.gtm-SUCCEEDED { background: #2fa84f44; } .gtm-FAILED, .gtm-ABORTED { background: #e5484d44; }
.gtm-lines { white-space: pre-wrap; font-family: ui-monospace, monospace; font-size: 12px; }
.gtm-feedback { font-size: 12px; opacity: 0.85; }
.gtm a { color: inherit; }
`;

function el(tag, attrs, children) {
  const node = document.createElement(tag);
  Object.entries(attrs || {}).forEach(([k, v]) => {
    if (k === "text") {
      node.textContent = v;
    } else {
      node.setAttribute(k, v);
    }
  });
  (children || []).forEach((c) => node.appendChild(c));
  return node;
}

function initPanel(context) {
  const saved = context.initialState || {};
  const settings = {
    namespace: saved.namespace ?? "/georg",
    burrUrl: saved.burrUrl ?? "http://localhost:7241",
  };
  let names = model.serviceNames(settings.namespace);
  let lastStatus;

  const style = el("style", { text: CSS });
  const missionSelect = el("select", { title: "mission" });
  const refreshBtn = el("button", { text: "↻", title: "reload mission list" });
  const startBtn = el("button", { text: "Start" });
  const abortBtn = el("button", { text: "Abort" });
  const stateBox = el("span", { class: "gtm-state gtm-IDLE", text: "NO STATUS" });
  const lines = el("div", { class: "gtm-lines" });
  const link = el("a", { target: "_blank", rel: "noreferrer" });
  const feedback = el("div", { class: "gtm-feedback" });
  const root = el("div", { class: "gtm" }, [
    style,
    el("div", { class: "gtm-row" }, [missionSelect, refreshBtn, startBtn, abortBtn]),
    el("div", {}, [stateBox]),
    lines,
    link,
    feedback,
  ]);
  context.panelElement.appendChild(root);

  function say(text) {
    feedback.textContent = `${new Date().toLocaleTimeString()}  ${text}`;
  }

  function render() {
    const d = model.describeStatus(lastStatus);
    stateBox.textContent = d.state;
    stateBox.className = `gtm-state gtm-${d.state}`;
    lines.textContent = d.lines.join("\n");
    const url = model.burrUrl(settings.burrUrl, lastStatus?.mission_id, lastStatus?.burr_app_id);
    link.textContent = url ? "open run in Burr UI" : "";
    if (url) {
      link.setAttribute("href", url);
    } else {
      link.removeAttribute("href");
    }
    abortBtn.disabled = !d.running;
  }

  async function call(service, request) {
    if (typeof context.callService !== "function") {
      throw new Error("this data source does not support services (use foxglove_bridge)");
    }
    return context.callService(service, request);
  }

  async function loadMissions() {
    try {
      const options = model.missionOptions(await call(names.list, {}));
      const previous = missionSelect.value;
      missionSelect.replaceChildren(...options.map((o) => el("option", { value: o.id, text: o.label })));
      if (options.some((o) => o.id === previous)) {
        missionSelect.value = previous;
      }
      say(`${options.length} missions`);
    } catch (err) {
      say(`mission list: ${err.message ?? err}`);
    }
  }

  startBtn.onclick = async () => {
    try {
      say(model.describeResponse("start", await call(names.start, model.startRequest(missionSelect.value))));
    } catch (err) {
      say(`start: ${err.message ?? err}`);
    }
  };
  abortBtn.onclick = async () => {
    try {
      say(model.describeResponse("abort", await call(names.cancel, model.cancelRequest(""))));
    } catch (err) {
      say(`abort: ${err.message ?? err}`);
    }
  };
  refreshBtn.onclick = loadMissions;

  function applySettings() {
    names = model.serviceNames(settings.namespace);
    context.saveState({ ...settings });
    context.subscribe([{ topic: names.status }]);
    context.updatePanelSettingsEditor({
      actionHandler: (action) => {
        if (action.action === "update") {
          const key = action.payload.path[1];
          settings[key] = action.payload.value;
          applySettings();
          loadMissions();
        }
      },
      nodes: {
        general: {
          label: "Georg Task Manager",
          fields: {
            namespace: { label: "Robot namespace", input: "string", value: settings.namespace },
            burrUrl: { label: "Burr UI URL", input: "string", value: settings.burrUrl },
          },
        },
      },
    });
  }

  context.onRender = (renderState, done) => {
    const frame = renderState.currentFrame || [];
    for (const event of frame) {
      if (event.topic === names.status) {
        lastStatus = event.message; // MissionStatus, updated on every Burr step
      }
    }
    render();
    done();
  };
  context.watch("currentFrame");
  applySettings();
  render();
  loadMissions();

  return () => {
    context.panelElement.replaceChildren();
  };
}

function activate(extensionContext) {
  extensionContext.registerPanel({ name: "Georg Task Manager", initPanel });
}

module.exports = { activate };
