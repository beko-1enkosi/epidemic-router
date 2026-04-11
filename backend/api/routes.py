from flask import Blueprint, jsonify, request

from backend.core.graph_logic import EpidemicGraph
from backend.core.data_stream import generate_proxy_signal, generate_normal_signal

router_bp = Blueprint("router", __name__)

graph = EpidemicGraph()

ANOMALY_DISTRICTS = [
    "Clinic_B", "Clinic_C", "Clinic_F",
    "District_C", "Village_D", "Village_G",
]


@router_bp.route("/api/state", methods=["GET"])
def get_state():
    """Return the current graph state."""
    return jsonify(graph.get_graph_state())


@router_bp.route("/api/inject", methods=["POST"])
def inject_anomaly():
    """Inject a high-risk proxy signal and recalculate the route."""
    signal = generate_proxy_signal(ANOMALY_DISTRICTS)
    graph.update_risk(signal["district"], signal["risk_score"])
    route = graph.get_optimal_route("Hub_A", "Outpost_E")

    return jsonify({
        "signal": signal,
        "optimal_route": route,
    })


@router_bp.route("/api/inject-normal", methods=["POST"])
def inject_normal():
    """Inject a low-risk signal simulating stable conditions."""
    signal = generate_normal_signal(graph.get_districts())
    graph.update_risk(signal["district"], signal["risk_score"])
    route = graph.get_optimal_route("Hub_A", "Outpost_E")

    return jsonify({
        "signal": signal,
        "optimal_route": route,
    })


@router_bp.route("/api/reset", methods=["POST"])
def reset():
    """Reset all district risk scores to baseline."""
    graph.reset_risks()
    return jsonify({
        "status": "reset",
        "message": "All districts restored to baseline risk.",
        "state": graph.get_graph_state(),
    })


@router_bp.route("/api/route", methods=["GET"])
def get_route():
    """Return the optimal route between any two districts."""
    source = request.args.get("source", "Hub_A")
    target = request.args.get("target", "Outpost_E")

    result = graph.get_optimal_route(source, target)
    status_code = 400 if "error" in result else 200

    return jsonify(result), status_code