import uuid
from typing import Dict, Any, Optional
from api.api.graph import Graph
from api.api.base_visualizer import BaseVisualizer
from graph_platform.platform.data_source_loader import DataSourceLoader
from graph_platform.platform.search_service import SearchService
from graph_platform.platform.filter_service import FilterService
from graph_platform.platform.cli_service import CLIService

# IMPORTUJEMO NOVE KLASE
# (Pazi da su fajlovi workspace.py i workspace_manager.py u istom folderu kao graph_manager.py)
from graph_platform.platform.workspace import Workspace
from graph_platform.platform.workspace_manager import WorkspaceManager

class GraphManager:
    _instance = None 

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GraphManager, cls).__new__(cls)
            
            # 1. Loaders
            cls._instance.data_source_loader = DataSourceLoader()
            cls._instance.data_source_loader.load_plugins([
                "data_source_json.data_source_json", 
                "data_source_csv.data_source_csv"
            ])
            cls._instance._cache = {} 
            cls._instance.visualizer = None

            # 2. Services
            cls._instance.search_service = SearchService()
            cls._instance.filter_service = FilterService()

            cls._instance.cli_service = CLIService()

            # 3. Workspace Manager
            cls._instance.workspace_manager = WorkspaceManager()
            
            # Backward compatibility (da ne puca ako neko trazi stare atribute)
            cls._instance.initial_graph = None
            cls._instance.current_graph = None

        # --- SIGURNOSNA ZAKRPA ---
        # Ako je instanca vec postojala (od pre izmena koda), 
        # rucno dodajemo workspace_manager ako fali.
        if not hasattr(cls._instance, 'workspace_manager'):
            cls._instance.workspace_manager = WorkspaceManager()
        
        # Takodje proveravamo da li servisi postoje
        if not hasattr(cls._instance, 'search_service'):
            cls._instance.search_service = SearchService()
        if not hasattr(cls._instance, 'filter_service'):
            cls._instance.filter_service = FilterService()
            
        return cls._instance

    def get_data_source_loader(self):
        return self.data_source_loader

    # --- WORKSPACE METODE ---
    
    def create_workspace(self, plugin_name: str, params: Dict[str, Any]) -> Workspace:
        try:
            plugin_instance = self.data_source_loader.get_plugin(plugin_name)
        except KeyError:
            raise ValueError(f"Plugin '{plugin_name}' nije pronađen.")

        graph = plugin_instance.parse(params)
        
        if not isinstance(graph, Graph):
            raise TypeError(f"Plugin '{plugin_name}' nije vratio validan Graph objekat.")

        # Ime workspace-a na osnovu fajla
        path_str = params.get('path', 'Unknown')
        # Pokusaj da izvuces samo ime fajla (radi i za Windows i za Linux putanje)
        ws_name = path_str.replace('\\', '/').split('/')[-1]
        
        new_workspace = Workspace(name=ws_name, original_graph=graph, source_plugin=plugin_name, source_params=params)
        
        self.workspace_manager.create_workspace(new_workspace)
        self.workspace_manager.set_active_workspace(new_workspace.id)
        
        return new_workspace

    def switch_workspace(self, workspace_id: str):
        self.workspace_manager.set_active_workspace(workspace_id)

    def delete_workspace(self, workspace_id: str):
        self.workspace_manager.delete_workspace(workspace_id)
        
    def get_workspaces_info(self):
        return self.workspace_manager.get_all_workspaces()

    # --- GLAVNE OPERACIJE ---

    def load_graph_from_source(self, plugin_name: str, params: Dict[str, Any]) -> Graph:
        # Wrapper zbog kompatibilnosti
        ws = self.create_workspace(plugin_name, params)
        return ws.current_graph

    def set_visualizer(self, visualizer: BaseVisualizer):
        self.visualizer = visualizer

    def render(self, graph: Graph = None):
        if not self.visualizer:
            raise RuntimeError("Nije postavljen nijedan vizualizer.")

        # Ako graf nije prosledjen, uzmi iz aktivnog workspace-a
        if graph is None:
            active_ws = self.workspace_manager.get_active_workspace()
            if not active_ws:
                raise RuntimeError("Nijedan workspace nije aktivan.")
            graph_to_render = active_ws.current_graph
        else:
            graph_to_render = graph
        
        if hasattr(self.visualizer, 'check_graph_compatibility'):
             self.visualizer.check_graph_compatibility(graph_to_render)

        return self.visualizer.render(graph_to_render)
    
    def apply_search(self, query: str) -> Graph:
        active_ws = self.workspace_manager.get_active_workspace()
        if not active_ws:
            raise RuntimeError("Nijedan workspace nije aktivan.")

        result_graph = self.search_service.search(active_ws.current_graph, query)
        
        active_ws.current_graph = result_graph
        active_ws.active_search_query = query
        return active_ws.current_graph
    
    def apply_cli_command(self, query:str) -> Graph:
        active_ws = self.workspace_manager.get_active_workspace()
        if not active_ws:
            raise RuntimeError("Nijedan workspace nije aktivan.")

        result_graph = self.cli_service.execute_command(active_ws.current_graph, query)
        
        active_ws.current_graph = result_graph
        return active_ws.current_graph
    
    def apply_filter(self, attribute: str, operator: str, value: Any) -> Graph:
        active_ws = self.workspace_manager.get_active_workspace()
        if not active_ws:
            raise RuntimeError("Nijedan workspace nije aktivan.")

        result_graph = self.filter_service.apply_filter(
            active_ws.current_graph, attribute, operator, value
        )
        
        active_ws.current_graph = result_graph
        active_ws.active_filters.append({'attribute': attribute, 'operator': operator, 'value': value})
        return active_ws.current_graph

    def reset_graph(self) -> Graph:
        active_ws = self.workspace_manager.get_active_workspace()
        if not active_ws:
            raise RuntimeError("Nijedan workspace nije aktivan.")

        active_ws.reset()
        return active_ws.current_graph