from flask import Blueprint, jsonify, request
from backend.core.graph_logic import EpidemicGraph
from backend.core.data_stream import generate_proxy_signal, generate_normal_signal

router_bp = Blueprint('router', __name__)

graph = EpidemicGraph()
DISTRICTS = [
    "Hub_A", "Hub_B",
    "Clinic_B", "Clinic_C", "Clinic_F",
    "District_C", "Village_D", "Village_G",
    "Outpost_E", "Outpost_H"
]

ANOMALY_DISTRICTS = [
    "Clinic_B", "Clinic_C", "Clinic_F",
    "District_C", "Village_D", "Village_G"
]
@router_bp.route('/api/state', methods=['GET'])
def get_state():
    """Returns current graph state — nodes + risk scores."""
    nodes = {n: data for n, data in graph.graph.nodes(data=True)}
    edges = [{"source": u, "target": v, "distance": d['distance']}
             for u, v, d in graph.graph.edges(data=True)]
    return jsonify({"nodes": nodes, "edges": edges})

@router_bp.route('/api/inject', methods=['POST'])
def inject_anomaly():
    """Fires a high-risk proxy signal into a mid-network district and recalculates route."""
    signal = generate_proxy_signal(ANOMALY_DISTRICTS)
    graph.update_risk(signal['district'], signal['risk_score'])
    route = graph.get_optimal_route("Hub_A", "Outpost_E")
    return jsonify({"signal": signal, "optimal_route": route})

@router_bp.route('/api/inject-normal', methods=['POST'])
def inject_normal():
    """Fires a low-risk signal simulating stable network conditions."""
    signal = generate_normal_signal(DISTRICTS)
    graph.update_risk(signal['district'], signal['risk_score'])
    route = graph.get_optimal_route("Hub_A", "Outpost_E")
    return jsonify({"signal": signal, "optimal_route": route})

@router_bp.route('/api/reset', methods=['POST'])
def reset():
    """Resets all districts to baseline risk."""
    global graph
    graph = EpidemicGraph()
    return jsonify({"status": "reset", "message": "Graph restored to baseline."})

@router_bp.route('/api/route', methods=['GET'])
def get_route():
    """Returns optimal route between any two districts."""
    source = request.args.get('source', 'Hub_A')
    target = request.args.get('target', 'Outpost_E')
    return jsonify(graph.get_optimal_route(source, target))