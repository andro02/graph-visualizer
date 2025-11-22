import csv
from api.api.graph import Node, Edge, Graph


class CSVDataSource:
    """
    CSV format (jedan fajl):

    id,label,target,weight
    A,Start,B,5
    B,End,,
    C,Middle,A,2
    """

    def __init__(self, csv_path: str, graph_name: str = "CSV Graph"):
        self.csv_path = csv_path
        self.graph_name = graph_name

    def load(self) -> Graph:
        nodes = {}
        edges = []

        with open(self.csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                node_id = row["id"]
                label = row.get("label", node_id)

                # Kreiraj node ako još ne postoji
                if node_id not in nodes:
                    nodes[node_id] = Node(node_id, label)

                # Ako postoji target — kreiraj edge
                target = row.get("target")
                if target and target.strip():
                    weight = float(row.get("weight", 1) or 1)

                    # Kreiraj target node ako nije u CSV-u kao poseban red
                    if target not in nodes:
                        nodes[target] = Node(target, target)

                    edges.append(Edge(node_id, target, weight))

        g = Graph(self.graph_name)
        g.nodes = list(nodes.values())
        g.edges = edges

        return g
