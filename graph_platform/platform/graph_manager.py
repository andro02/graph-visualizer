from typing import Dict, Any, Optional
from api.api.graph import Graph
from api.api.base_visualizer import BaseVisualizer
from graph_platform.platform.data_source_loader import DataSourceLoader

class GraphManager:
    """
    Core servis platforme.
    """
    _instance = None # Singleton pattern

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GraphManager, cls).__new__(cls)
            # Inicijalizacija Loadera
            cls._instance.data_source_loader = DataSourceLoader()
            # Ucitavanje poznatih plugina
            cls._instance.data_source_loader.load_plugins([
                "data_source_json.data_source_json", 
                "data_source_csv.data_source_csv"
            ])
            cls._instance._cache = {}
            cls.visualizer: Optional[BaseVisualizer] = None
        return cls._instance

    def get_data_source_loader(self):
        return self.data_source_loader

    def load_graph_from_source(self, plugin_name: str, params: Dict[str, Any]) -> Graph:
        """
        Učitava graf koristeći Loader da nađe plugin.
        """
        cache_key = f"{plugin_name}_{params.get('path', '')}" 
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            plugin_instance = self.data_source_loader.get_plugin(plugin_name)
        except KeyError:
            raise ValueError(f"Plugin '{plugin_name}' nije pronađen ili registrovan.")

        graph = plugin_instance.parse(params)

        if not isinstance(graph, Graph):
            raise TypeError(f"Plugin '{plugin_name}' nije vratio validan Graph objekat.")

        self._cache[cache_key] = graph
        return graph

    def set_visualizer(self, visualizer: BaseVisualizer):
        self.visualizer = visualizer

    def render(self, graph: Graph):
        if not self.visualizer:
            raise RuntimeError("Nije postavljen nijedan vizualizer.")
        
        if hasattr(self.visualizer, 'check_graph_compatibility'):
             self.visualizer.check_graph_compatibility(graph)

        return self.visualizer.render(graph)