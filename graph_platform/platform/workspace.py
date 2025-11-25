import uuid
# Pazite na import, prilagodite putanju ako vam je drugacija
# Pretpostavljam da je Graph u api.api.graph
from api.api.graph import Graph

class Workspace:
    def __init__(self, name: str, original_graph: Graph, source_plugin: str, source_params: dict):
        self.id = str(uuid.uuid4())
        self.name = name
        
        # Podaci o izvoru
        self.source_plugin = source_plugin
        self.source_params = source_params

        # Stanje grafa
        self.initial_graph = original_graph
        self.current_graph = original_graph

        # Istorija promena
        self.active_search_query = None
        self.active_filters = []
        # Ovde pamtimo koji vizualizator koristi OVAJ workspace
        self.selected_visualizer = "Simple Visualizer" # Default vrednost

    def set_current_graph(self, graph: Graph):
        self.current_graph = graph

    def reset(self):
        """Vraća workspace na početno stanje."""
        self.current_graph = self.initial_graph
        self.active_search_query = None
        self.active_filters = []