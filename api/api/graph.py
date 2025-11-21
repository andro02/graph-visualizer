from typing import Any, Dict, List

class Node:
    def __init__(self, id: str, label: str = "", data: Dict[str, Any] = None):
        self.id = id
        self.label = label
        self.data = data or {}

    def to_dict(self):
        return {
            "id": self.id,
            "label": self.label,
            "data": self.data,
        }


class Edge:
    def __init__(self, source: str, target: str, weight: float = 1.0, data: Dict[str, Any] = None):
        self.source = source
        self.target = target
        self.weight = weight
        self.data = data or {}

    def to_dict(self):
        return {
            "source": self.source,
            "target": self.target,
            "weight": self.weight,
            "data": self.data,
        }


class Graph:
    def __init__(self, name: str = None, nodes: List[Node] = None, edges: List[Edge] = None):
        self.name = name
        self.nodes = nodes or []
        self.edges = edges or []

    def add_node(self, node: Node):
        self.nodes.append(node)

    def add_edge(self, edge: Edge):
        self.edges.append(edge)

    def to_dict(self):
        return {
            "name": self.name,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
        }
