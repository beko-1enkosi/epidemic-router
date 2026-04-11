const WIDTH = 1000;
const HEIGHT = 560;

const POSITIONS = {
  Hub_A:      { x: 130, y: 260 },
  Hub_B:      { x: 130, y: 450 },
  Clinic_B:   { x: 320, y: 160 },
  Clinic_C:   { x: 480, y: 290 },
  Clinic_F:   { x: 320, y: 450 },
  District_C: { x: 620, y: 90 },
  Village_D:  { x: 620, y: 350 },
  Village_G:  { x: 480, y: 480 },
  Outpost_E:  { x: 840, y: 160 },
  Outpost_H:  { x: 840, y: 420 },
};

const ICONS = {
  Hub_A: "✳",
  Hub_B: "✳",
  Clinic_B: "🏥",
  Clinic_C: "🏥",
  Clinic_F: "🏥",
  District_C: "🏠",
  Village_D: "🏘",
  Village_G: "🏘",
  Outpost_E: "📡",
  Outpost_H: "📡",
};

let activePath = [];

const svg = d3.select("#graph-container")
  .append("svg")
  .attr("viewBox", `0 0 ${WIDTH} ${HEIGHT}`)
  .style("max-height", "400px");

const linkGroup = svg.append("g");
const nodeGroup = svg.append("g");

function riskColor(risk) {
  if (risk >= 0.7) return "#ff4444";
  if (risk >= 0.4) return "#ffaa00";
  return "#00ff88";
}

function edgeKey(d) {
  return [d.source, d.target].sort().join("-");
}

function isPathEdge(source, target) {
  for (let i = 0; i < activePath.length - 1; i += 1) {
    const a = activePath[i];
    const b = activePath[i + 1];
    if ((a === source && b === target) || (a === target && b === source)) {
      return true;
    }
  }
  return false;
}

function setText(id, value) {
  document.getElementById(id).textContent = value;
}

function setRiskDisplay(value, color) {
  const el = document.getElementById("stat-risk");
  el.textContent = value;
  el.style.color = color;
}

function setStatus(message, isAlert = false) {
  const bar = document.getElementById("status-bar");
  bar.textContent = message;
  bar.className = isAlert ? "status-bar alert" : "status-bar";
}

function toggleResetButton(show) {
  document.getElementById("btn-reset").style.display = show ? "inline-block" : "none";
}

function generateSignalId(prefix) {
  return `${prefix}-${Math.floor(Math.random() * 9000 + 1000)}`;
}

function logTerminal(message) {
  const feed = document.getElementById("terminal-feed");
  const now = new Date().toLocaleTimeString();

  const line = document.createElement("div");
  line.className = "terminal-line";
  line.textContent = `[${now}] ${message}`;

  feed.prepend(line);

  while (feed.children.length > 8) {
    feed.removeChild(feed.lastChild);
  }
}

function resetUiState() {
  setText("stat-id", "—");
  setRiskDisplay("—", "#00ff88");
  setText("stat-topology", "Standard");
  setStatus("Signal Verified. System Nominal.");
  toggleResetButton(false);
}

function updateUiFromSignal(signal, isAnomaly) {
  setText("stat-id", generateSignalId(isAnomaly ? "PX" : "NS"));
  setRiskDisplay(`${Math.round(signal.risk_score * 100)}%`, isAnomaly ? "#ff4444" : "#00ff88");
  setText("stat-topology", isAnomaly ? "Bypass" : "Standard");

  if (isAnomaly) {
    setStatus(`⚠ High Risk Anomaly at ${signal.district}. Rerouting...`, true);
    toggleResetButton(true);
    logTerminal(JSON.stringify({
      origin: "Hub_A",
      dest: "Outpost_E",
      proxy_detect: signal.district,
      risk: signal.risk_score,
      action: "RE_ROUTE_TRIGGERED",
    }));
  } else {
    setStatus("Signal Verified. Using Standard Optimal Route.");
    toggleResetButton(false);
    logTerminal(JSON.stringify({
      origin: "Hub_A",
      dest: "Outpost_E",
      risk: signal.risk_score,
      action: "STANDARD_FORWARD",
    }));
  }
}

function render(graphData) {
  const nodes = Object.entries(graphData.nodes).map(([id, data]) => ({ id, ...data }));
  const edges = graphData.edges;

  const links = linkGroup.selectAll(".link").data(edges, edgeKey);

  links.enter()
    .append("line")
    .attr("class", "link")
    .merge(links)
    .attr("x1", d => POSITIONS[d.source].x)
    .attr("y1", d => POSITIONS[d.source].y)
    .attr("x2", d => POSITIONS[d.target].x)
    .attr("y2", d => POSITIONS[d.target].y)
    .attr("class", d => `link${isPathEdge(d.source, d.target) ? " active-path" : ""}`);

  links.exit().remove();

  const nodeSelection = nodeGroup.selectAll(".node").data(nodes, d => d.id);

  const nodeEnter = nodeSelection.enter()
    .append("g")
    .attr("class", "node")
    .attr("transform", d => `translate(${POSITIONS[d.id].x},${POSITIONS[d.id].y})`);

  nodeEnter.append("circle").attr("r", 38);
  nodeEnter.append("text").attr("y", 4).attr("class", "icon");
  nodeEnter.append("text").attr("y", 56).attr("class", "name-label");
  nodeEnter.append("text").attr("y", -44).attr("class", "risk-label");

  const allNodes = nodeSelection.merge(nodeEnter);

  allNodes
    .attr("transform", d => `translate(${POSITIONS[d.id].x},${POSITIONS[d.id].y})`);

  allNodes.select("circle")
    .attr("fill", d => (d.risk >= 0.7 ? "#2a0808" : "#0a1a2a"))
    .attr("stroke", d => riskColor(d.risk));

  allNodes.select(".icon")
    .text(d => ICONS[d.id] || "•");

  allNodes.select(".name-label")
    .text(d => d.id.replace(/_/g, " ").toUpperCase());

  allNodes.select(".risk-label")
    .text(d => `Risk: ${Math.round(d.risk * 100)}%`)
    .attr("fill", d => riskColor(d.risk));

  nodeSelection.exit().remove();
}

async function loadState() {
  try {
    const response = await fetch("/api/state");
    const data = await response.json();
    render(data);
  } catch (error) {
    console.error("Failed to load graph state:", error);
    setStatus("System error: unable to load graph state.", true);
  }
}

async function triggerNormal() {
  try {
    const response = await fetch("/api/inject-normal", { method: "POST" });
    const data = await response.json();

    activePath = data.optimal_route.path || [];
    updateUiFromSignal(data.signal, false);
    await loadState();
  } catch (error) {
    console.error("Failed to generate normal signal:", error);
    setStatus("System error: failed to generate normal signal.", true);
  }
}

async function triggerAnomaly() {
  try {
    const response = await fetch("/api/inject", { method: "POST" });
    const data = await response.json();

    activePath = data.optimal_route.path || [];
    updateUiFromSignal(data.signal, true);
    await loadState();
  } catch (error) {
    console.error("Failed to inject anomaly:", error);
    setStatus("System error: failed to inject anomaly.", true);
  }
}

async function resetSystem() {
  try {
    await fetch("/api/reset", { method: "POST" });
    activePath = [];
    resetUiState();
    logTerminal("System reset. All districts restored to baseline.");
    await loadState();
  } catch (error) {
    console.error("Failed to reset system:", error);
    setStatus("System error: failed to reset the system.", true);
  }
}

resetUiState();
loadState();