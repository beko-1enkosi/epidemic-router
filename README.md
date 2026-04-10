# 🦠 Anticipatory Epidemic Routing Engine

> **ALGOfest Hackathon 2026 — HealthTech Track**  
> *Proactive outbreak response through real-time graph optimization*

---

## The Problem

In fragile or under-resourced health systems, outbreak response is **reactive**. By the time a cluster is confirmed and mobile clinics are dispatched, the window for containment has already closed. Supply routes are planned using static maps, not live risk data.

This kills people.

## The Solution

The **Anticipatory Epidemic Routing Engine** monitors a network of districts for environmental proxy signals, anomalies in water quality, pharmacy purchase spikes, sanitation failures, and uses **dynamic graph optimization** to instantly recalculate the safest and most efficient dispatch routes *before* an outbreak is confirmed.

When a district's risk score spikes, the algorithm doesn't wait. It reroutes.

---

## Live Demo

🌐 **[epidemic-router-demo.onrender.com](https://epidemic-router-demo.onrender.com/)**

| State | Behaviour |
|-------|-----------|
| 🟢 Normal | Dijkstra routes mobile clinics via the shortest path |
| 🔴 Anomaly Detected | Risk score spikes → algorithm recalculates → bypass route highlighted |
| ♻️ Reset | All districts restored to 10% baseline risk |

---

## Algorithmic Core

This project is built around **Dijkstra's Algorithm with composite dynamic edge weights**:

```
edge_weight = distance × (1 + destination_risk)
```

This means the algorithm does not just optimize for distance — it treats high-risk districts as heavier nodes, naturally routing around outbreak clusters or prioritizing them for rapid dispatch depending on the use case.

### Example Output

```bash
NORMAL:        Hub_A → Clinic_B → District_C → Outpost_E  (cost: 33.0)
AFTER ANOMALY: Hub_A → Clinic_B → Outpost_E               (cost: 44.0)
```

The algorithm **willingly paid 11 extra cost units** to avoid District_C when its risk spiked to 95%. That is dynamic re-routing in action.

---

## Architecture

```
epidemic-router/
├── backend/
│   ├── core/
│   │   ├── graph_logic.py      # NetworkX graph + dynamic Dijkstra
│   │   └── data_stream.py      # Proxy anomaly signal generator
│   ├── api/
│   │   └── routes.py           # Flask API endpoints
│   ├── static/
│   │   ├── main.js             # D3.js graph visualization
│   │   └── style.css           # Terminal UI styling
│   ├── templates/
│   │   └── index.html          # Frontend shell
│   └── server.py               # Flask entry point
├── tests/
│   └── test_graph.py           # unit tests (unittest)
├── requirements.txt
└── README.md
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Graph Engine | NetworkX | District graph + Dijkstra routing |
| Backend | Flask | API endpoints + template serving |
| Visualization | D3.js v7 | Live interactive graph rendering |
| Signal Simulation | Python (random, datetime) | Proxy anomaly data stream |
| Testing | unittest | TDD on core algorithm |

---

## API Reference

### `GET /api/state`
Returns the current graph — all nodes with risk scores and all edges with distances.

```json
{
  "nodes": { "District_C": { "risk": 0.95 }, "..." : "..." },
  "edges": [{ "source": "Hub_A", "target": "Clinic_B", "distance": 10 }]
}
```

### `POST /api/inject`
Fires a random high-risk proxy signal (risk: 0.6–0.99) into a district and returns the recalculated optimal route.

```json
{
  "signal": {
    "district": "District_C",
    "risk_score": 0.92,
    "trigger": "Water quality drop detected",
    "timestamp": "2026-04-10T11:21:50+00:00"
  },
  "optimal_route": {
    "path": ["Hub_A", "Clinic_B", "Outpost_E"],
    "cost": 44.0
  }
}
```

### `POST /api/inject-normal`
Fires a low-risk signal (risk: 0.05–0.2) simulating stable conditions.

### `POST /api/reset`
Resets all district risk scores to baseline (0.1).

### `GET /api/route?source=Hub_A&target=Outpost_E`
Returns the current optimal route between any two districts.

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- pip

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/beko-1enkosi/epidemic-router
cd epidemic-router

# 2. Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
python -m backend.server
```

Visit `http://localhost:5000` in your browser.

---

## Running Tests

```bash
python -m unittest tests.test_graph -v
```

Expected output: **17 tests passing**, covering:
- Graph structure integrity
- Baseline risk validation
- Risk update correctness
- Dijkstra normal routing
- Anomaly bypass routing
- Cost increase verification after anomaly injection

---

## Proxy Signal Types

The system simulates four real-world early-warning indicators:

| Signal | Real-World Analogy |
|--------|--------------------|
| Water quality drop detected | Municipal water contamination sensor |
| Pharmacy purchase spike | Unusual OTC medication demand |
| Reported case cluster | Community health worker field report |
| Sanitation failure logged | Waste management system alert |

---


## Real-World Applicability

This prototype is designed with South African public health infrastructure in mind:

- **Rural clinic dispatch** — optimizing mobile health unit routing across underserved districts
- **TB/HIV outbreak containment** — early proxy detection before case confirmation
- **Water-borne disease prevention** — sanitation sensor integration as anomaly triggers
- **Community Health Worker coordination** — algorithmic support for CHW routing decisions

---

## Team

| Name | Role |
|------|------|
| *Thobeka Nkosi* | Full-Stack Developer & Algorithm Design |

---

## License

MIT License — open for adaptation by public health organizations.

---

*Built for ALGOfest Hackathon 2026 — HealthTech Track from Devpost*