const WIDTH = 620, HEIGHT = 400;
const POSITIONS = {
  Hub_A:      { x: 100, y: 200 },
  Clinic_B:   { x: 240, y: 200 },
  District_C: { x: 380, y: 110 },
  Village_D:  { x: 380, y: 290 },
  Outpost_E:  { x: 520, y: 200 },
};
const ICONS = {
  Hub_A: "✳", Clinic_B: "🏥", District_C: "🏠", Village_D: "🏘", Outpost_E: "📡"
};

let nodes = [], edges = [], activePath = [];

const svg = d3.select("#graph-container").append("svg")
  .attr("viewBox", `0 0 ${WIDTH} ${HEIGHT}`)
  .style("max-height", "380px");
  
const linkGroup = svg.append("g");
const nodeGroup = svg.append("g");

function riskColor(risk) {
  if (risk >= 0.7) return "#ff4444";
  if (risk >= 0.4) return "#ffaa00";
  return "#00ff88";
}

function isPathEdge(source, target) {
  for (let i = 0; i < activePath.length - 1; i++) {
    const a = activePath[i], b = activePath[i + 1];
    if ((a === source && b === target) || (a === target && b === source)) return true;
  }
  return false;
}

function render(graphData) {
  nodes = Object.entries(graphData.nodes).map(([id, d]) => ({ id, ...d }));
  edges = graphData.edges;

  // Links
  const links = linkGroup.selectAll(".link").data(edges, d => d.source + d.target);
  links.enter().append("line").attr("class", "link")
    .merge(links)
    .attr("x1", d => POSITIONS[d.source].x)
    .attr("y1", d => POSITIONS[d.source].y)
    .attr("x2", d => POSITIONS[d.target].x)
    .attr("y2", d => POSITIONS[d.target].y)
    .attr("class", d => "link" + (isPathEdge(d.source, d.target) ? " active-path" : ""));

  // Nodes
  const nodeEl = nodeGroup.selectAll(".node").data(nodes, d => d.id);
  const enter = nodeEl.enter().append("g").attr("class", "node")
    .attr("transform", d => `translate(${POSITIONS[d.id].x},${POSITIONS[d.id].y})`);
  enter.append("circle").attr("r", 28);
  enter.append("text").attr("y", 4).attr("class", "icon");
  enter.append("text").attr("y", 44).attr("class", "name-label");
  enter.append("text").attr("y", -34).attr("class", "risk-label");

  const all = nodeEl.merge(enter);
  all.attr("transform", d => `translate(${POSITIONS[d.id].x},${POSITIONS[d.id].y})`);
  all.select("circle")
    .attr("fill", d => d.risk >= 0.7 ? "#2a0808" : "#0a1a2a")
    .attr("stroke", d => riskColor(d.risk));
  all.select(".icon").text(d => ICONS[d.id]);
  all.select(".name-label").text(d => d.id.replace("_", " ").toUpperCase());
  all.select(".risk-label").text(d => `Risk: ${Math.round(d.risk * 100)}%`)
    .attr("fill", d => riskColor(d.risk));
}

function logTerminal(msg) {
  const feed = document.getElementById("terminal-feed");
  const now = new Date().toLocaleTimeString();
  const line = document.createElement("div");
  line.className = "terminal-line";
  line.textContent = `[${now}] ${msg}`;
  feed.prepend(line);
  if (feed.children.length > 8) feed.removeChild(feed.lastChild);
}

async function loadState() {
  const res = await fetch("/api/state");
  const data = await res.json();
  render(data);
}

async function triggerNormal() {
  const res = await fetch("/api/inject-normal", { method: "POST" });
  const data = await res.json();
  activePath = data.optimal_route.path;
  const sig = data.signal;
  document.getElementById("stat-id").textContent = "NS-" + Math.floor(Math.random()*9000+1000);
  document.getElementById("stat-risk").textContent = Math.round(sig.risk_score * 100) + "%";
  document.getElementById("stat-risk").style.color = "#00ff88";
  document.getElementById("stat-topology").textContent = "Standard";
  document.getElementById("status-bar").textContent = "Signal Verified. Using Standard Optimal Route.";
  document.getElementById("status-bar").className = "status-bar";
  logTerminal(JSON.stringify({ origin: "Hub_A", dest: "Outpost_E", risk: sig.risk_score, action: "STANDARD_FORWARD" }));
  document.getElementById("btn-reset").style.display = "none";
  await loadState();
}

async function triggerAnomaly() {
  const res = await fetch("/api/inject", { method: "POST" });
  const data = await res.json();
  activePath = data.optimal_route.path;
  const sig = data.signal;
  document.getElementById("stat-id").textContent = "PX-" + Math.floor(Math.random()*9000+1000);
  document.getElementById("stat-risk").textContent = Math.round(sig.risk_score * 100) + "%";
  document.getElementById("stat-risk").style.color = "#ff4444";
  document.getElementById("stat-topology").textContent = "Bypass";
  document.getElementById("status-bar").textContent = `⚠ High Risk Anomaly at ${sig.district}. Rerouting...`;
  document.getElementById("status-bar").className = "status-bar alert";
  logTerminal(JSON.stringify({ origin: "Hub_A", dest: "Outpost_E", proxy_detect: sig.district, risk: sig.risk_score, action: "RE_ROUTE_TRIGGERED" }));
  document.getElementById("btn-reset").style.display = "inline-block";
  await loadState();
}

async function resetSystem() {
  await fetch("/api/reset", { method: "POST" });
  activePath = [];
  document.getElementById("stat-id").textContent = "—";
  document.getElementById("stat-risk").textContent = "—";
  document.getElementById("stat-risk").style.color = "#00ff88";
  document.getElementById("stat-topology").textContent = "Standard";
  document.getElementById("status-bar").textContent = "Signal Verified. System Nominal.";
  document.getElementById("status-bar").className = "status-bar";
  document.getElementById("btn-reset").style.display = "none";
  logTerminal("System reset. All districts restored to baseline.");
  await loadState();
}

// Initial load
loadState();