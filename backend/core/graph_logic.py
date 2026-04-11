import networkx as nx

class EpidemicGraph:
    """
    A mathematical graph representation of medical districts and connecting routes.
    Uses dynamically weighted edges to calculate optimal paths based on distance 
    and real-time infection risk data.
    """

    def __init__(self):
        """Initializes the EpidemicGraph with an empty NetworkX graph and builds the baseline map."""
        self.graph = nx.Graph()
        self._build_baseline_map()

    def _build_baseline_map(self):
        districts = [
            "Hub_A", "Hub_B",
            "Clinic_B", "Clinic_C", "Clinic_F",
            "District_C", "Village_D", "Village_G",
            "Outpost_E", "Outpost_H"
        ]
        for district in districts:
            self.graph.add_node(district, risk=0.1)

        roads = [
            # Hub_A connections
            ("Hub_A", "Clinic_B", 10),
            ("Hub_A", "Village_D", 25),
            ("Hub_A", "Hub_B", 40),
            # Hub_B connections
            ("Hub_B", "Clinic_F", 12),
            ("Hub_B", "Village_G", 20),
            # Clinic_B connections
            ("Clinic_B", "District_C", 15),
            ("Clinic_B", "Outpost_E", 30),
            ("Clinic_B", "Clinic_C", 18),
            # Clinic_C connections
            ("Clinic_C", "District_C", 10),
            ("Clinic_C", "Outpost_H", 22),
            # Clinic_F connections
            ("Clinic_F", "Village_G", 8),
            ("Clinic_F", "Outpost_H", 25),
            # Village connections
            ("Village_D", "District_C", 10),
            ("Village_G", "Outpost_H", 15),
            # District/Outpost connections
            ("District_C", "Outpost_E", 5),
            ("Outpost_E", "Outpost_H", 20),
        ]

        for source, target, distance in roads:
            self.graph.add_edge(source, target, distance=distance)

    def get_graph_info(self):
        """
        Retrieves a raw summary of the graph's current nodes and edges.
        
        Returns:
            dict: A dictionary containing lists of nodes and edges with their associated data attributes.
        """
        return {
            "districts": list(self.graph.nodes(data=True)),
            "roads": list(self.graph.edges(data=True))
        }

    def update_risk(self, district, new_risk):
        """
        Updates the infection risk multiplier for a specific district.

        Args:
            district (str): The string identifier of the node to update.
            new_risk (float): The new risk value to assign to the node (typically between 0.0 and 1.0).

        Raises:
            ValueError: If the specified district does not exist in the graph.
        """
        if district not in self.graph.nodes:
            raise ValueError(f"District '{district}' not found.")
        self.graph.nodes[district]['risk'] = new_risk

    def get_optimal_route(self, source, target):
        """
        Calculates the safest and most efficient path between two nodes using Dijkstra's algorithm.
        
        The edge weight is dynamically calculated as: distance * (1 + risk of destination node).
        This ensures the algorithm routes around high-risk clusters when possible.

        Args:
            source (str): The starting node identifier.
            target (str): The destination node identifier.

        Returns:
            dict: A dictionary containing the calculated 'path' (list of nodes) and the 
                  total composite 'cost' (float). Returns an empty list and -1 cost if no path exists.
        """
        def composite_weight(u, v, edge_data):
            destination_risk = self.graph.nodes[v]['risk']
            return edge_data['distance'] * (1 + destination_risk)

        try:
            path = nx.dijkstra_path(
                self.graph, 
                source, 
                target, 
                weight=composite_weight
            )
            cost = nx.dijkstra_path_length(
                self.graph, 
                source, 
                target, 
                weight=composite_weight
            )
            return {"path": path, "cost": round(cost, 2)}
        except nx.NetworkXNoPath:
            return {"path": [], "cost": -1, "error": "No path found"}

    def get_graph_state(self):
        """
        Exports the entire graph data structure into a format suitable for JSON serialization.
        
        Returns:
            dict: A node-link data representation of the NetworkX graph, useful for frontend visualization.
        """
        return nx.node_link_data(self.graph)


if __name__ == "__main__":
    router = EpidemicGraph()
    
    # Test 1: Normal conditions
    print("NORMAL:", router.get_optimal_route("Hub_A", "Outpost_E"))
    
    # Test 2: Inject anomaly in District_C and re-route
    router.update_risk("District_C", 0.95)
    print("AFTER ANOMALY:", router.get_optimal_route("Hub_A", "Outpost_E"))