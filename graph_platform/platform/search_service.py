from api.api.graph import Graph, Node
from datetime import date, datetime

class SearchService:
    """
    Pretraga nad grafom: pretrazujemo label, nazive atributa i vrednosti atributa.
    """
    def search(self, graph: Graph, query: str) -> Graph:
        if not query:
            return graph 

        query_lower = query.lower()
        matched_nodes = []

        for node in graph.nodes:
            for key, value in node.data.items():

                if key.lower() == "id":
                    continue

                if query_lower in key.lower():
                    matched_nodes.append(node)
                    break

                if isinstance(value, (str, int, float)):
                    if query_lower in str(value).lower():
                        matched_nodes.append(node)
                        break

                elif isinstance(value, (date, datetime)):
                    if query_lower in value.isoformat().lower():
                        matched_nodes.append(node)
                        break

        new_graph = Graph(name=f"{graph.name} (search)", directed=graph.directed)
        new_graph.nodes = matched_nodes

        node_ids = {n.id for n in matched_nodes}
        new_graph.edges = [
            e for e in graph.edges
            if e.source in node_ids and e.target in node_ids
        ]

        return new_graph
