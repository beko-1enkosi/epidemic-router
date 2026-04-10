from flask import Blueprint, jsonify, request
from backend.core.graph_logic import EpidemicGraph
from backend.core.data_stream import generate_proxy_signal, generate_normal_signal

router_bp = Blueprint('router', __name__)

# Single shared graph instance
graph = EpidemicGraph()
DISTRICTS = ["Hub_A", "Clinic_B", "District_C", "Village_D", "Outpost_E"]

@router_bp.route('/api/state', methods=['GET'])
def get_state():
    """Returns current graph state — nodes + risk scores."""

    nodes = {n: data for n, data in graph.graph.nodes(data=True)}
    edges = [{"source": u, "target": v, "distance": d['distance']} 
             for u, v, d in graph.graph.edges(data=True)]
    return jsonify({"nodes": nodes, "edges": edges})

@router_bp.route('/api/inject', methods=['POST'])
def inject_anomaly():
    """Injects a random proxy signal and updates the graph."""

    signal = generate_proxy_signal(DISTRICTS)
    graph.update_risk(signal['district'], signal['risk_score'])
    route = graph.get_optimal_route("Hub_A", signal['district'])
    return jsonify({"signal": signal, "optimal_route": route})

@router_bp.route('/api/inject-normal', methods=['POST'])
def inject_normal():
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
    """Get optimal route between two districts."""
    
    source = request.args.get('source', 'Hub_A')
    target = request.args.get('target', 'Outpost_E')
    return jsonify(graph.get_optimal_route(source, target))