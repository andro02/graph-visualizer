import unittest
from typing import List, Dict, Any
from .data_source import DataSourcePlugin, PluginParameter, PluginParameterType
from .graph import Graph

class ConcreteDataSource(DataSourcePlugin):
    """
    Ispravna implementacija plugin-a za testiranje.
    """
    def name(self) -> str:
        return "Test Plugin"

    def get_parameters(self) -> List[PluginParameter]:
        return [
            PluginParameter("path", "Path to file", PluginParameterType.FILE)
        ]

    def parse(self, parameters: Dict[str, Any]) -> Graph:
        return Graph()

class IncompleteDataSource(DataSourcePlugin):
    """
    Neispravna implementacija (fali parse).
    """
    def name(self) -> str:
        return "Incomplete Plugin"

    def get_parameters(self) -> List[PluginParameter]:
        return []

class TestDataSourceInterface(unittest.TestCase):

    def test_cannot_instantiate_abstract_class(self):
        with self.assertRaises(TypeError):
            DataSourcePlugin()

    def test_cannot_instantiate_incomplete_subclass(self):
        with self.assertRaises(TypeError):
            IncompleteDataSource()

    def test_can_instantiate_concrete_subclass(self):
        plugin = ConcreteDataSource()
        self.assertIsInstance(plugin, DataSourcePlugin)
        self.assertEqual(plugin.name(), "Test Plugin")
        
        params = plugin.get_parameters()
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0].name, "path")

        result_graph = plugin.parse({})
        self.assertIsInstance(result_graph, Graph)

    def test_plugin_parameter_structure(self):
        param1 = PluginParameter("api_key", "Twitter API Key", PluginParameterType.TEXT, True, "12345")
        self.assertEqual(param1.name, "api_key")
        self.assertEqual(param1.type, PluginParameterType.TEXT)
        self.assertTrue(param1.is_required)
        self.assertEqual(param1.default_value, "12345")

    def test_parameter_types_enum(self):
        self.assertEqual(PluginParameterType.FILE.value, "file")
        self.assertEqual(PluginParameterType.TEXT.value, "text")

if __name__ == '__main__':
    unittest.main()