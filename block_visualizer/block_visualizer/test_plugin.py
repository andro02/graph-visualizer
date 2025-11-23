import unittest
from api.api.graph import Graph, Node, Edge
from api.api.base_visualizer import BaseVisualizer
from block_visualizer.block_visualizer.plugin import BlockVisualizer

class TestBlockVisualizer(unittest.TestCase):
    
    def setUp(self):
        self.plugin = BlockVisualizer()
        self.graph = Graph()
        
        # ima labelu i dodatni podatak
        self.n1 = Node(id="N1", label="Baza Podataka", data={"type": "PostgreSQL", "port": 5432})
        # nema labelu (koristi se ID)
        self.n2 = Node(id="N2", label="", data={"type": "Web Server"})
        
        self.graph.add_node(self.n1)
        self.graph.add_node(self.n2)
        
        # edge koristi stringove za source i target
        self.edge = Edge(source="N2", target="N1") 
        self.graph.add_edge(self.edge)

    def test_inheritance(self):
        """
        Proverava da li plugin ispravno nasledjuje BaseVisualizer.
        Ovo je kljucno da bi ga Loader prepoznao.
        """
        self.assertIsInstance(self.plugin, BaseVisualizer)

    def test_render_output_type(self):
        """Proverava da li metoda render vraca string."""
        html = self.plugin.render(self.graph)
        self.assertIsInstance(html, str)
        self.assertTrue(len(html) > 0)

    def test_render_blocks_structure(self):
        """
        Proverava da li HTML sadrzi elemente koji cine 'blokove'.
        Acceptance Criteria: 'Lepljenje nodova u blokove'
        """
        html = self.plugin.render(self.graph)
        
        self.assertIn("<div", html)
        self.assertIn("border:", html)
        self.assertIn("display: flex", html) # Flexbox za raspored blokova

    def test_render_content_accuracy(self):
        """Proverava da li su podaci iz grafa tacno preneti u HTML."""
        html = self.plugin.render(self.graph)
        
        self.assertIn("Baza Podataka", html) # Labela N1
        self.assertIn("N2", html)            # ID N2 (jer nema labelu)
        
        # atributi
        self.assertIn("PostgreSQL", html)
        self.assertIn("5432", html)
        
        # veze
        self.assertIn("N2", html)
        self.assertIn("&rarr;", html) # Strelica
        self.assertIn("N1", html)

    def test_empty_graph(self):
        """Proverava ponacanje sa praznim grafom."""
        empty = Graph()
        html = self.plugin.render(empty)
        # ne sme da pukne
        self.assertIn("prazan", html)

if __name__ == '__main__':
    unittest.main()