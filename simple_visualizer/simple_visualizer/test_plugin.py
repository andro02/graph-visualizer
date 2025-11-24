import unittest
from api.api.graph import Graph, Node, Edge
from api.api.base_visualizer import BaseVisualizer
from .plugin import SimpleVisualizer

class TestSimpleVisualizer(unittest.TestCase):
    
    def setUp(self):
        self.plugin = SimpleVisualizer()
        self.graph = Graph()
        
        n1 = Node(id="A", label="Start")
        n2 = Node(id="B", label="End")
        self.graph.add_node(n1)
        self.graph.add_node(n2)
        
        self.graph.add_edge(Edge("A", "B"))

    def test_inheritance(self):
        """Provera da li je pravi tip plugina."""
        self.assertIsInstance(self.plugin, BaseVisualizer)

    def test_name(self):
        """Provera imena (dobro je za debug)."""
        self.assertEqual(self.plugin.name(), "Simple Visualizer")

    def test_render_structure(self):
        """Provera da li renderuje HTML sa krugovima."""
        html = self.plugin.render(self.graph)
        
        # Provera da je string i nije prazan
        self.assertIsInstance(html, str)
        self.assertTrue(len(html) > 0)
        
        # Provera CSS-a za krug
        self.assertIn("border-radius: 50%", html)
        
        # Provera sadrzaja
        self.assertIn("Start", html)
        self.assertIn("End", html)
        self.assertIn("A &mdash; B", html) # Provera prikaza veze

if __name__ == '__main__':
    unittest.main()