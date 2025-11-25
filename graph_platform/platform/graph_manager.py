from typing import Dict, Any, Optional
from api.api.graph import Graph
from api.api.base_visualizer import BaseVisualizer
from graph_platform.platform.data_source_loader import DataSourceLoader
from graph_platform.platform.search_service import SearchService
from graph_platform.platform.filter_service import FilterService

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

            # Search / Filter servisi
            cls._instance.search_service = SearchService()
            cls._instance.filter_service = FilterService()

            # Inicijalni i trenutni graf
            cls._instance.initial_graph = None
            cls._instance.current_graph = None

        return cls._instance

    def get_data_source_loader(self):
        return self.data_source_loader

    def load_graph_from_source(self, plugin_name: str, params: Dict[str, Any]) -> Graph:
        """
        Učitava graf koristeći Loader da nađe plugin.
        """
        cache_key = f"{plugin_name}_{params.get('path', '')}" 
        if cache_key in self._cache:
            self.initial_graph = self._cache[cache_key]
            self.current_graph = self.initial_graph
            return self._cache[cache_key]

        try:
            plugin_instance = self.data_source_loader.get_plugin(plugin_name)
        except KeyError:
            raise ValueError(f"Plugin '{plugin_name}' nije pronađen ili registrovan.")

        graph = plugin_instance.parse(params)

        if not isinstance(graph, Graph):
            raise TypeError(f"Plugin '{plugin_name}' nije vratio validan Graph objekat.")
        
        # Sačuvaj inicijalni i trenutni graf
        self.initial_graph = graph
        self.current_graph = graph

        self._cache[cache_key] = graph
        return graph

    def set_visualizer(self, visualizer: BaseVisualizer):
        self.visualizer = visualizer

    def render(self, graph: Graph):
        if not self.visualizer:
            raise RuntimeError("Nije postavljen nijedan vizualizer.")

        graph_to_render = self.current_graph or self.initial_graph
        if graph_to_render is None:
            raise RuntimeError("Nijedan graf nije učitan.")
        
        if hasattr(self.visualizer, 'check_graph_compatibility'):
             self.visualizer.check_graph_compatibility(graph_to_render)

        return self.visualizer.render(graph_to_render)
    
    def apply_search(self, query: str) -> Graph:
        if not self.current_graph:
            raise RuntimeError("Nijedan graf nije učitan.")

        self.current_graph = self.search_service.search(self.current_graph, query)
        return self.current_graph

    def apply_filter(self, attribute: str, operator: str, value: Any) -> Graph:
        if not self.current_graph:
            raise RuntimeError("Nijedan graf nije učitan.")

        self.current_graph = self.filter_service.apply_filter(
            self.current_graph, attribute, operator, value
        )
        return self.current_graph

    def reset_graph(self) -> Graph:
        if self.initial_graph is None:
            raise RuntimeError("Nijedan graf nije učitan.")

        self.current_graph = self.initial_graph
        return self.current_graph