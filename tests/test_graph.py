import unittest
from backend.core.graph_logic import EpidemicGraph

class TestEpidemicGraph(unittest.TestCase):

    def setUp(self):
        """Fresh graph instance before each test."""
        self.graph = EpidemicGraph()

    # --- Graph Structure Tests ---

    def test_correct_number_of_nodes(self):
        """Graph should have exactly 10 district nodes."""
        self.assertEqual(len(self.graph.graph.nodes), 10)

    def test_correct_number_of_edges(self):
        """Graph should have exactly 16 road connections."""
        self.assertEqual(len(self.graph.graph.edges), 16)

    def test_all_nodes_exist(self):
        """All expected district names should be present."""
        expected = {
            "Hub_A", "Hub_B",
            "Clinic_B", "Clinic_C", "Clinic_F",
            "District_C", "Village_D", "Village_G",
            "Outpost_E", "Outpost_H"
        }
        self.assertEqual(set(self.graph.graph.nodes), expected)

    def test_baseline_risk_is_ten_percent(self):
        """All nodes should start with a baseline risk of 0.1."""
        for node, data in self.graph.graph.nodes(data=True):
            self.assertAlmostEqual(data['risk'], 0.1, msg=f"{node} has wrong baseline risk")

    def test_edges_have_distance_attribute(self):
        """Every edge must have a 'distance' attribute."""
        for u, v, data in self.graph.graph.edges(data=True):
            self.assertIn('distance', data, msg=f"Edge {u}-{v} missing distance")

    # --- update_risk Tests ---

    def test_update_risk_valid_district(self):
        """Risk score should update correctly for a valid district."""
        self.graph.update_risk("District_C", 0.95)
        self.assertAlmostEqual(self.graph.graph.nodes["District_C"]['risk'], 0.95)

    def test_update_risk_invalid_district_raises(self):
        """Updating a non-existent district should raise ValueError."""
        with self.assertRaises(ValueError):
            self.graph.update_risk("Fake_Zone", 0.9)

    def test_update_risk_does_not_affect_other_nodes(self):
        """Updating one node's risk should leave all others unchanged."""
        self.graph.update_risk("District_C", 0.9)
        for node, data in self.graph.graph.nodes(data=True):
            if node != "District_C":
                self.assertAlmostEqual(data['risk'], 0.1, msg=f"{node} was incorrectly modified")

    # --- get_optimal_route Tests ---

    def test_normal_route_returns_path(self):
        """Should return a valid path under normal conditions."""
        result = self.graph.get_optimal_route("Hub_A", "Outpost_E")
        self.assertIn("path", result)
        self.assertGreater(len(result["path"]), 0)

    def test_normal_route_starts_and_ends_correctly(self):
        """Path must start at Hub_A and end at Outpost_E."""
        result = self.graph.get_optimal_route("Hub_A", "Outpost_E")
        self.assertEqual(result["path"][0], "Hub_A")
        self.assertEqual(result["path"][-1], "Outpost_E")

    def test_normal_route_uses_district_c(self):
        """Under normal conditions, shortest path should pass through District_C."""
        result = self.graph.get_optimal_route("Hub_A", "Outpost_E")
        self.assertIn("District_C", result["path"])

    def test_anomaly_reroutes_away_from_high_risk_node(self):
        """After a high-risk anomaly, path should avoid the spiked district."""
        self.graph.update_risk("District_C", 0.99)
        result = self.graph.get_optimal_route("Hub_A", "Outpost_E")
        self.assertNotIn("District_C", result["path"])

    def test_anomaly_reroute_still_reaches_destination(self):
        """Rerouted path must still reach Outpost_E even after anomaly."""
        self.graph.update_risk("District_C", 0.99)
        result = self.graph.get_optimal_route("Hub_A", "Outpost_E")
        self.assertEqual(result["path"][-1], "Outpost_E")

    def test_cost_increases_after_anomaly(self):
        """Bypass route cost should be higher than the normal optimal cost."""
        normal_cost = self.graph.get_optimal_route("Hub_A", "Outpost_E")["cost"]
        self.graph.update_risk("District_C", 0.99)
        anomaly_cost = self.graph.get_optimal_route("Hub_A", "Outpost_E")["cost"]
        self.assertGreater(anomaly_cost, normal_cost)

    def test_same_source_and_target_returns_trivial_path(self):
        """Routing from a node to itself should return a single-node path."""
        result = self.graph.get_optimal_route("Hub_A", "Hub_A")
        self.assertEqual(result["path"], ["Hub_A"])

    def test_route_returns_cost_as_float(self):
        """Cost should always be a numeric value."""
        result = self.graph.get_optimal_route("Hub_A", "Outpost_E")
        self.assertIsInstance(result["cost"], float)

    # --- Reset Behaviour (via re-instantiation) ---

    def test_reinstantiation_resets_risk(self):
        """Creating a new EpidemicGraph should always start at baseline risk."""
        self.graph.update_risk("District_C", 0.99)
        fresh_graph = EpidemicGraph()
        self.assertAlmostEqual(fresh_graph.graph.nodes["District_C"]['risk'], 0.1)


if __name__ == '__main__':
    unittest.main(verbosity=2)