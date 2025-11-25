from api.api.graph import Graph, Node

class SearchService:
    """
    Implementacija pretrage nad grafom.
    """
    def search(self, graph: Graph, query: str) -> Graph:
        """
        Traži čvorove čiji atributi sadrže query tekst.
        Vraća novi podgraf.
        """
        query_lower = query.lower()
        matched_nodes = []

        for node in graph.nodes:
            # Proveri label i sve atribute
            if query_lower in node.label.lower():
                matched_nodes.append(node)
                continue

            for v in node.data.values():
                if isinstance(v, str) and query_lower in v.lower():
                    matched_nodes.append(node)
                    break
                elif isinstance(v, (int, float)) and query_lower in str(v):
                    matched_nodes.append(node)
                    break

        # Kreiraj novi podgraf
        new_graph = Graph(name=f"{graph.name} (search)")
        new_graph.nodes = matched_nodes

        # Dodaj samo edge-ove između čvorova koji postoje u matched_nodes
        node_ids = {n.id for n in matched_nodes}
        new_graph.edges = [e for e in graph.edges if e.source in node_ids and e.target in node_ids]

        return new_graph
