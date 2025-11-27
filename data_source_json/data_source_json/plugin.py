#json plugin
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
        graph.directed = True # Bitno za usmerene cikluse

        # Da li je ovo format koji podrzava cikluse
        if isinstance(data, dict) and "nodes" in data and "links" in data:
            self._parse_flat_format(graph, data)
        else:
            self.parsed_nodes = {} 
            self.parse_recursive(graph, data, "root")
        
        return graph

    def _parse_flat_format(self, graph: Graph, data: Dict[str, Any]):
        """
        Parser za format koji eksplicitno definise cvorove i veze.
        Ovaj format omogucava cikluse (npr. A->B->A).
        """
        # Ucitavanje cvorova
        for node_data in data.get("nodes", []):
            node_id = str(node_data.get("id"))
            node_label = node_data.get("label", node_id)
            
            node = Node(id=node_id)
            node.label = node_label
            
            # Sve ostalo ide u data atribute
            for k, v in node_data.items():
                if k not in ["id", "label"]:
                    node.data[k] = v
            
            graph.add_node(node)

        # Ucitavanje veza
        for link_data in data.get("links", []):
            source_id = str(link_data.get("source"))
            target_id = str(link_data.get("target"))
            
            # Provera da li cvorovi postoje pre kreiranja veze
            source_exists = any(n.id == source_id for n in graph.nodes)
            target_exists = any(n.id == target_id for n in graph.nodes)

            if source_exists and target_exists:
                # Izdvajamo atribute veze
                edge_data = {k: v for k, v in link_data.items() if k not in ["source", "target"]}
                
                edge = Edge(source=source_id, target=target_id, data=edge_data)
                graph.add_edge(edge)

    def parse_recursive(self, graph: Graph, data: Any, current_id: str) -> Node:
        # Provera ID-a unutar podataka (ako postoji @id polje, ono ima prednost)
        if isinstance(data, dict) and "@id" in data:
            current_id = data["@id"]
        
        #ako je vec kreiran cvor sa ovim ID-jem, vracamo ga
        if current_id in self.parsed_nodes:
            return self.parsed_nodes[current_id]

        node = Node(id=current_id)
        # Pokusaj da nadjes labelu ili name u podacima
        if isinstance(data, dict):
            if "name" in data: node.label = data["name"]
            elif "label" in data: node.label = data["label"]
            else: node.label = current_id
        else:
            node.label = current_id

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
        # pomocna fja za kreiranje grane
        def create_edge(target):
            s_id = str(source_node.id)
            t_id = str(target.id)
            edge = Edge(source=s_id, target=t_id, data={"relation": relation_name})
            graph.add_edge(edge)

        if isinstance(value, list):
            for i, item in enumerate(value):
                child_id = None
                if isinstance(item, dict):
                    child_id = item.get("@id")
                
                # ako nema @id, generišemo ga na osnovu roditelja
                if not child_id:
                    child_id = f"{source_node.id}_{relation_name}_{i}"

                target_node = self.parse_recursive(graph, item, child_id)
                create_edge(target_node)
        else:
            child_id = None
            if isinstance(value, dict):
                child_id = value.get("@id")            
            if not child_id:
                child_id = f"{source_node.id}_{relation_name}"

            target_node = self.parse_recursive(graph, value, child_id)
            create_edge(target_node)