import networkx as nx


class EpidemicGraph:
    """
    Graph model of medical districts and connected routes.

    Each edge uses a dynamic composite weight:
        distance * (1 + destination_risk)

    This allows the routing engine to prefer safer paths when a district's
    risk score increases.
    """

    BASELINE_RISK = 0.1

    DISTRICTS = [
        "Hub_A", "Hub_B",
        "Clinic_B", "Clinic_C", "Clinic_F",
        "District_C", "Village_D", "Village_G",
        "Outpost_E", "Outpost_H",
    ]

    ROADS = [
        ("Hub_A", "Clinic_B", 10),
        ("Hub_A", "Village_D", 25),
        ("Hub_A", "Hub_B", 40),
        ("Hub_B", "Clinic_F", 12),
        ("Hub_B", "Village_G", 20),
        ("Clinic_B", "District_C", 15),
        ("Clinic_B", "Outpost_E", 30),
        ("Clinic_B", "Clinic_C", 18),
        ("Clinic_C", "District_C", 10),
        ("Clinic_C", "Outpost_H", 22),
        ("Clinic_F", "Village_G", 8),
        ("Clinic_F", "Outpost_H", 25),
        ("Village_D", "District_C", 10),
        ("Village_G", "Outpost_H", 15),
        ("District_C", "Outpost_E", 5),
        ("Outpost_E", "Outpost_H", 20),
    ]

    def __init__(self):
        self.graph = nx.Graph()
        self._build_baseline_map()

    def _build_baseline_map(self) -> None:
        for district in self.DISTRICTS:
            self.graph.add_node(district, risk=self.BASELINE_RISK)

        for source, target, distance in self.ROADS:
            self.graph.add_edge(source, target, distance=distance)

    def get_districts(self) -> list[str]:
        return list(self.graph.nodes)

    def get_graph_info(self) -> dict:
        return {
            "districts": list(self.graph.nodes(data=True)),
            "roads": list(self.graph.edges(data=True)),
        }

    def update_risk(self, district: str, new_risk: float) -> None:
        if district not in self.graph:
            raise ValueError(f"District '{district}' not found.")

        if not 0.0 <= new_risk <= 1.0:
            raise ValueError("Risk score must be between 0.0 and 1.0.")

        self.graph.nodes[district]["risk"] = round(float(new_risk), 2)

    def reset_risks(self) -> None:
        for district in self.graph.nodes:
            self.graph.nodes[district]["risk"] = self.BASELINE_RISK

    def _composite_weight(self, u: str, v: str, edge_data: dict) -> float:
        destination_risk = self.graph.nodes[v]["risk"]
        return edge_data["distance"] * (1 + destination_risk)

    def get_optimal_route(self, source: str, target: str) -> dict:
        if source not in self.graph:
            return {"path": [], "cost": -1.0, "error": f"Unknown source node: {source}"}

        if target not in self.graph:
            return {"path": [], "cost": -1.0, "error": f"Unknown target node: {target}"}

        try:
            path = nx.dijkstra_path(
                self.graph,
                source,
                target,
                weight=self._composite_weight,
            )
            cost = nx.dijkstra_path_length(
                self.graph,
                source,
                target,
                weight=self._composite_weight,
            )
            return {"path": path, "cost": round(float(cost), 2)}
        except nx.NetworkXNoPath:
            return {"path": [], "cost": -1.0, "error": "No path found"}

    def get_graph_state(self) -> dict:
        nodes = {node: data for node, data in self.graph.nodes(data=True)}
        edges = [
            {"source": u, "target": v, "distance": data["distance"]}
            for u, v, data in self.graph.edges(data=True)
        ]
        return {"nodes": nodes, "edges": edges}


if __name__ == "__main__":
    router = EpidemicGraph()

    print("NORMAL:", router.get_optimal_route("Hub_A", "Outpost_E"))

    router.update_risk("District_C", 0.95)
    print("AFTER ANOMALY:", router.get_optimal_route("Hub_A", "Outpost_E"))