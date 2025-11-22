import csv
import os
from typing import Dict, Any, List
from api.api.data_source import DataSourcePlugin, PluginParameter, PluginParameterType
from api.api.graph import Node, Edge, Graph

class CSVDataSource(DataSourcePlugin):
    """
    CSV format (jedan fajl) implementiran u skladu sa DataSourcePlugin API-jem.
    """

    def name(self) -> str:
        return "CSV Data Source Loader"

    def get_parameters(self) -> List[PluginParameter]:
        return [
            PluginParameter(
                name="csv_path",
                description="Putanja do CSV fajla",
                type=PluginParameterType.FILE
            ),
            PluginParameter(
                name="graph_name",
                description="Naziv grafa",
                type=PluginParameterType.TEXT,
                is_required=False,
                default_value="CSV Graph"
            )
        ]

    def parse(self, parameters: Dict[str, Any]) -> Graph:
        csv_path = parameters["csv_path"]
        graph_name = parameters.get("graph_name", "CSV Graph")

        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV fajl nije pronađen: {csv_path}")

        nodes = {}
        edges = []

        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                node_id = row["id"]
                label = row.get("label", node_id)

                if node_id not in nodes:
                    nodes[node_id] = Node(id=node_id, label=label, data={"id": node_id, "label": label})

                target = row.get("target")
                if target and target.strip():
                    weight = float(row.get("weight", 1) or 1)
                    if target not in nodes:
                        nodes[target] = Node(id=target, label=target, data={"id": target, "label": target})
                    edges.append(Edge(source=node_id, target=target, weight=weight))

        g = Graph(name=graph_name)
        for node in nodes.values():
            g.add_node(node)
        for edge in edges:
            g.add_edge(edge)

        return g
