import unittest
import json
import os
from api.api.graph import Graph
from data_source_json.data_source_json.plugin import JSONDataSource

class TestJSONDataSource(unittest.TestCase):
    
    def setUp(self):
        self.plugin = JSONDataSource()
        self.test_file = "test_data.json"
        
        self.dummy_data = {
            "name": "Test Root",
            "age": 30,
            "children": [
                {"name": "Child 1", "age": 5},
                {"name": "Child 2", "age": 8}
            ]
        }
        with open(self.test_file, 'w') as f:
            json.dump(self.dummy_data, f)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_name(self):
        self.assertEqual(self.plugin.name(), "JSON Data Source")

    def test_parse_valid_json(self):
        params = {"path": self.test_file}
        graph = self.plugin.parse(params)
        self.assertIsInstance(graph, Graph)

    def test_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            self.plugin.parse({"path": "nepostojeci_fajl.json"})

if __name__ == '__main__':
    unittest.main()