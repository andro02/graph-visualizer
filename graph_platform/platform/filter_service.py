from typing import Any
from api.api.graph import Graph, Node

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

        for node in graph.nodes:
            attr_value = node.data.get(attribute)
            if attr_value is None:
                continue

            # Pokušaj da kastuje value u tip atributa
            try:
                if isinstance(attr_value, int):
                    cast_value = int(value)
                elif isinstance(attr_value, float):
                    cast_value = float(value)
                else:
                    cast_value = str(value)
            except ValueError:
                raise ValueError(f"Vrednost '{value}' ne može biti konvertovana u tip atributa '{type(attr_value).__name__}'")

            if op_func(attr_value, cast_value):
                matched_nodes.append(node)

        # Kreiraj novi podgraf
        new_graph = Graph(name=f"{graph.name} (filter)")
        new_graph.nodes = matched_nodes

        node_ids = {n.id for n in matched_nodes}
        new_graph.edges = [e for e in graph.edges if e.source in node_ids and e.target in node_ids]

        return new_graph
