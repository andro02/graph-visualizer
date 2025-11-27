from typing import Any, Dict, List
from datetime import datetime

def parse_value(value):
    """Automatski pokušava da pretvori value u int, float, date, ili ostavi kao string."""
    if isinstance(value, (int, float, datetime)):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except:
            pass
        try:
            return float(value)
        except:
            pass
        try:
            return datetime.fromisoformat(value)
        except:
            pass
    return value 

class Node:
    def __init__(self, id: str, label: str = "", data: Dict[str, Any] = None):
        self.id = id
        self.label = label
        self.data = {k: parse_value(v) for k, v in (data or {}).items()}

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
        self.data = {k: parse_value(v) for k, v in (data or {}).items()}

    def to_dict(self):
        return {
            "source": self.source,
            "target": self.target,
            "weight": self.weight,
            "data": self.data,
        }


class Graph:
    def __init__(self, name: str = None, directed: bool = True, nodes: List[Node] = None, edges: List[Edge] = None):
        self.name = name
        self.directed = directed
        self.nodes = nodes or []
        self.edges = edges or []

    def add_node(self, node: Node):
        if any(n.id == node.id for n in self.nodes):
            print(f"Node {node.id} already exists!")
            return
        self.nodes.append(node)
        print(f"Node {node.id} added.")

    def add_edge(self, edge: Edge):
        if any(e.source == edge.source and e.target == edge.target for e in self.edges):
            print(f"Edge from {edge.source} to {edge.target} already exists!")
            return
        if not any(n.id == edge.source for n in self.nodes) or not any(n.id == edge.target for n in self.nodes):
            print("Both nodes must exist to add edge!")
            return
        self.edges.append(edge)
        print(f"Edge from {edge.source} to {edge.target} added.")

    def to_dict(self):
        return {
            "name": self.name,
            "directed": self.directed,
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
        }
    
    def edit_node(self, node_id, **properties):
        node = self.nodes.get(node_id)
        if not node:
            print(f"Node {node_id} does not exist!")
            return
        node.properties.update(properties)
        print(f"Updated node {node_id}")

    def delete_node(self, node_id):
        node = self.nodes.get(node_id)
        if not node:
            print(f"Node {node_id} does not exist!")
            return
        if node.edges:
            print(f"Cannot delete node {node_id}, it has connected edges: {node.edges}")
            return
        del self.nodes[node_id]
        print(f"Deleted node {node_id}")

    def edit_edge(self, edge_id, **properties):
        edge = self.edges.get(edge_id)
        if not edge:
            print(f"Edge {edge_id} does not exist!")
            return
        edge.properties.update(properties)
        print(f"Updated edge {edge_id}")

    def delete_edge(self, edge_id):
        edge = self.edges.get(edge_id)
        if not edge:
            print(f"Edge {edge_id} does not exist!")
            return
        node1_id, node2_id = edge.nodes
        self.nodes[node1_id].edges.discard(edge_id)
        self.nodes[node2_id].edges.discard(edge_id)
        del self.edges[edge_id]
        print(f"Deleted edge {edge_id}")

    
    def filter_nodes(self, condition):
        # Ovo je jednostavan filter, može se proširiti
        filtered = []
        for node in self.nodes.values():
            try:
                if eval(condition, {}, node.properties):
                    filtered.append(node)
            except Exception as e:
                pass
        print(f"Filtered nodes: {filtered}")

    def search_nodes(self, key, value):
        result = [node for node in self.nodes.values() if node.properties.get(key) == value]
        print(f"Search result: {result}")

    def clear_graph(self):
        self.nodes.clear()
        self.edges.clear()
        print("Cleared entire graph")
