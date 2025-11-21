from api.graph import Node, Edge, Graph

def test_graph_models():
    print("➡️ Test: Kreiranje nodova i ivica")

    # Node test
    n1 = Node(id="A", label="Start")
    n2 = Node(id="B", label="End")

    # Edge test
    e1 = Edge(source="A", target="B", weight=5)

    # Graph test
    g = Graph()
    g.add_node(n1)
    g.add_node(n2)
    g.add_edge(e1)

    print("Nodes:", g.nodes)
    print("Edges:", g.edges)

    assert len(g.nodes) == 2, "❌ Graph nema 2 čvora"
    assert len(g.edges) == 1, "❌ Graph nema 1 ivicu"

    # Test serializer
    g_dict = g.to_dict()

    print("Serialized graph:", g_dict)

    assert "nodes" in g_dict
    assert "edges" in g_dict

    print("✅ Svi osnovni testovi prošli!")
    

if __name__ == "__main__":
    test_graph_models()
