import os
import json
from typing import Dict, Any, List
from api.api.data_source import DataSourcePlugin, PluginParameter, PluginParameterType
from api.api.graph import Graph

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

        graph = Graph(directed=True)
        
        return graph