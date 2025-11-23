import os
import unittest
from api.api.graph import Graph
from data_source_csv.data_source_csv.plugin import CSVDataSourceLoader

class TestCSVDataSource(unittest.TestCase):
    
    def setUp(self):
        # Root folder projekta
        base_dir = os.path.dirname(os.path.dirname(__file__))
        self.csv_path = os.path.join(base_dir, "data_source_csv", "data", "sample_graph.csv")
        self.plugin = CSVDataSourceLoader()

    def test_name(self):
        self.assertEqual(self.plugin.name(), "CSV Data Source Loader")

    def test_parse_csv_graph(self):
        if not os.path.exists(self.csv_path):
            self.fail(f"CSV fajl nije pronađen: {self.csv_path}")
        
        params = {"csv_path": self.csv_path, "graph_name": "Sample CSV Graph"}
        graph: Graph = self.plugin.parse(params)

        # Test nodes
        node_ids = sorted([n.id for n in graph.nodes])
        self.assertSetEqual(set(node_ids), {"A", "B", "C"})

        # Test edges
        edge_pairs = sorted([(e.source, e.target, e.weight) for e in graph.edges])
        self.assertIn(("A", "B", 5.0), edge_pairs)
        self.assertIn(("C", "A", 2.0), edge_pairs)

        # Test graph name
        self.assertEqual(graph.name, "Sample CSV Graph")

if __name__ == "__main__":
    unittest.main()
