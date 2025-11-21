from enum import Enum
from typing import Any, List, Optional, Union
from datetime import datetime


class Node:
    def __init__(self, id: Any, attributes: dict = None):
        pass

class Edge:
    def __init__(self, source: Node, target: Node, attributes: dict = None):
        pass

class Graph:
    def __init__(self, directed: bool = True):
        pass

    def add_node(self, node: Node):
        pass

    def add_edge(self, edge: Edge):
        pass