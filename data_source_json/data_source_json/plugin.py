from typing import Dict, Any, List
from api.api.data_source import DataSourcePlugin, PluginParameter, PluginParameterType
from api.api.graph import Graph

class JSONDataSource(DataSourcePlugin):
    """
    Konkretna implementacija Data Source plugina za JSON fajlove.
    """

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
        # Za sada samo vraćamo prazan graf ili grešku, implementacija sledi
        raise NotImplementedError("Parsiranje još nije implementirano.")