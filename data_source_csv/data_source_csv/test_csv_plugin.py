import os
from data_source_csv.csv_data_source import CSVDataSource

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # root folder
CSV_PATH = os.path.join(BASE_DIR, "data_source_csv", "data", "sample_graph.csv")


def test_csv_plugin():
    print("➡️ Test: CSVDataSource učitavanje grafa iz data/sample_graph.csv")

    if not os.path.exists(CSV_PATH):
        raise FileNotFoundError(f"Nije pronađen CSV fajl: {CSV_PATH}")

    ds = CSVDataSource(CSV_PATH, graph_name="Sample CSV Graph")
    graph = ds.load()

    # Test nodes
    node_ids = sorted([n.id for n in graph.nodes])
    print("Nodes:", node_ids)
    assert set(node_ids) == {"A", "B", "C"}

    # Test edges
    edge_pairs = sorted([(e.source, e.target, e.weight) for e in graph.edges])
    print("Edges:", edge_pairs)
    assert ("A", "B", 5.0) in edge_pairs
    assert ("C", "A", 2.0) in edge_pairs

    # Test graph name
    print("Graph name:", graph.name)
    assert graph.name == "Sample CSV Graph"

    print("✅ CSV plugin test uspešno prošao!")


if __name__ == "__main__":
    test_csv_plugin()
