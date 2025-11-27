from typing import Any
from api.api.graph import Graph, Node, parse_value

class FilterService:
    """
    Implementacija filtera nad grafom.
    """
    OPERATORS = {
        "==": lambda a, b: a == b,
        "!=": lambda a, b: a != b,
        ">": lambda a, b: a > b,
        ">=": lambda a, b: a >= b,
        "<": lambda a, b: a < b,
        "<=": lambda a, b: a <= b,
    }

    def apply_filter(self, graph: Graph, attribute: str, operator: str, value: Any) -> Graph:
        if operator not in self.OPERATORS:
            raise ValueError(f"Nepoznat operator: {operator}")

        op_func = self.OPERATORS[operator]
        matched_nodes = []

        cast_value = parse_value(value)

        for node in graph.nodes:
            attr_value = node.data.get(attribute)
            if attr_value is None:
                continue

            if type(attr_value) != type(cast_value) and operator not in ["==", "!="]:
                continue

            try:
                if op_func(attr_value, cast_value):
                    matched_nodes.append(node)
            except Exception:
                continue

        # Kreiraj novi podgraf
        new_graph = Graph(name=f"{graph.name} (filter)", directed=graph.directed)
        new_graph.nodes = matched_nodes

        node_ids = {n.id for n in matched_nodes}
        new_graph.edges = [e for e in graph.edges if e.source in node_ids and e.target in node_ids]

        return new_graph
