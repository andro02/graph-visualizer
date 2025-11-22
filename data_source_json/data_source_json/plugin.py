import os
import json
from typing import Dict, Any, List
from api.api.data_source import DataSourcePlugin, PluginParameter, PluginParameterType
from api.api.graph import Graph, Node, Edge

class JSONDataSource(DataSourcePlugin):

    def name(self) -> str:
        return "JSON Data Source"

    def get_parameters(self) -> List[PluginParameter]:
        return [
            PluginParameter(
                name="path", 
                description="Putanja do JSON fajla", 
                type=PluginParameterType.FILE
            )
        ]

    def parse(self, parameters: Dict[str, Any]) -> Graph:
        path = parameters.get("path")
        if not path or not os.path.exists(path):
            raise FileNotFoundError(f"Fajl nije pronadjen na putanji: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        graph = Graph()
        self.parsed_nodes = {}  #za pracenje vec kreiranih cvorova
        
        # root -> id pocetnog cvora
        self.parse_recursive(graph, data, "root")
        
        return graph

    def parse_recursive(self, graph: Graph, data: Any, current_id: str) -> Node:
        # Provera ID-a unutar podataka (ako postoji @id polje, ono ima prednost)
        if isinstance(data, dict) and "@id" in data:
            current_id = data["@id"]
        
        #ako je vec kreiran cvor sa ovim ID-jem, vracamo ga
        if current_id in self.parsed_nodes:
            return self.parsed_nodes[current_id]

        node = Node(id=current_id)
        graph.add_node(node)
        self.parsed_nodes[current_id] = node

        if isinstance(data, dict):
            for key, value in data.items():
                if key == "@id": continue

                if isinstance(value, (dict, list)):
                    self.handle_complex_value(graph, node, key, value)
                else:
                    node.data[key] = value

        elif isinstance(data, list):
            for i, item in enumerate(data):
                self.handle_complex_value(graph, node, f"item_{i}", item)

        return node

    def handle_complex_value(self, graph: Graph, source_node: Node, relation_name: str, value: Any):
        # pomocna funkcija za kreiranje grane
        def create_edge(target):
            edge = Edge(source=source_node.id, target=target.id, data={"relation": relation_name})
            graph.add_edge(edge)

        if isinstance(value, list):
            for i, item in enumerate(value):
                child_id = item.get("@id") if isinstance(item, dict) else f"{source_node.id}_{relation_name}_{i}"
                target_node = self.parse_recursive(graph, item, child_id)
                create_edge(target_node)
        else:
            child_id = value.get("@id") if isinstance(value, dict) else f"{source_node.id}_{relation_name}"
            target_node = self.parse_recursive(graph, value, child_id)
            create_edge(target_node)