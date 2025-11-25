import os
import json
from pathlib import Path
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound

# Importi iz tvoje platforme
from graph_platform.platform.graph_manager import GraphManager
from graph_platform.platform.visualizer_loader import VisualizerLoader

class IndexView(View):
    def _get_context_data(self, selected_visualizer=None):
        """Priprema podatke za dropdown menije."""
        manager = GraphManager()
        loader = manager.get_data_source_loader()

        vis_loader = VisualizerLoader()
        
        # Ucitavanje default vizualizatora (hardcoded za potrebe projekta)
        try:
            from simple_visualizer.simple_visualizer.plugin import SimpleVisualizer
            vis_loader.register_visualizer(SimpleVisualizer().name(), SimpleVisualizer)
        except ImportError as e:
            print(f"Greska pri ucitavanju SimpleVisualizer: {e}")

        try:
            from block_visualizer.block_visualizer.plugin import BlockVisualizer
            vis_loader.register_visualizer(BlockVisualizer().name(), BlockVisualizer)
        except ImportError as e:
            print(f"Greska pri ucitavanju BlockVisualizer: {e}")
            
        visualizers = vis_loader.list_visualizers()
        
        # Ucitavanje pluginova
        known_plugins = ["data_source_json.data_source_json", "data_source_csv.data_source_csv"]
        loader.load_plugins(known_plugins)
        
        plugins = loader.get_available_plugins()
        
        # Skeniranje fajlova u direktorijumima pluginova
        files_map = {}
        # Pretpostavka putanje: views.py -> core -> graph_explorer -> (root) -> data_source...
        base_dir = Path(__file__).resolve().parent.parent.parent.parent
        
        plugin_paths = {
            "JSON Data Source": os.path.join(base_dir, "data_source_json", "data_source_json", "data"),
            "CSV Data Source":  os.path.join(base_dir, "data_source_csv", "data_source_csv", "data"),
        }

        for plugin_name in plugins:
            folder_path = plugin_paths.get(plugin_name)
            files_map[plugin_name] = []
            if folder_path and os.path.exists(folder_path):
                try:
                    for file in os.listdir(folder_path):
                        if os.path.isfile(os.path.join(folder_path, file)):
                            full_path = os.path.join(folder_path, file)
                            files_map[plugin_name].append({'name': file, 'path': full_path})
                except Exception:
                    pass

        return {
            "plugins": plugins,
            "files_map": files_map,
            "visualizers": visualizers,
            "selected_visualizer": selected_visualizer,
        }

    def get(self, request):
        context = self._get_context_data()
        return render(request, "core/index.html", context)

    def post(self, request):
        plugin_name = request.POST.get('plugin_name')
        file_path = request.POST.get('source_path')
        visualizer = request.POST.get('visualizer') 

        if not plugin_name or not file_path:
            messages.error(request, "Morate izabrati plugin i fajl!")
            context = self._get_context_data(selected_visualizer=visualizer)
            return render(request, "core/index.html", context)

        manager = GraphManager()
        try:
            # KREIRANJE WORKSPACE-A
            workspace = manager.create_workspace(plugin_name, {"path": file_path})

            if visualizer:
                workspace.selected_visualizer = visualizer
            
            messages.success(request, f"Workspace '{workspace.name}' kreiran!")
            
            context = self._get_context_data(selected_visualizer=visualizer)
            # KLJUČNO: Šaljemo ID workspace-a, a ne path
            context['graph_id'] = workspace.id 
            
            return render(request, "core/index.html", context)
            
        except Exception as e:
            messages.error(request, f"Greska pri ucitavanju: {str(e)}")
            import traceback
            traceback.print_exc() # Ispis greske u konzolu servera
        
        context = self._get_context_data(selected_visualizer=visualizer)
        return render(request, "core/index.html", context)


# --- API ENDPOINTS ---

def api_graphs(request):
    """Vraća listu workspace-ova (koristi se za kompatibilnost)."""
    manager = GraphManager()
    # Vraćamo ID-eve aktivnih workspace-ova
    workspaces = manager.workspace_manager.get_all_workspaces()
    ids = [w['id'] for w in workspaces]
    return JsonResponse({"graphs": ids})

def api_workspaces(request):
    """Vraca detaljnu listu svih workspace-ova za tabove."""
    manager = GraphManager()
    return JsonResponse({"workspaces": manager.get_workspaces_info()})

def api_switch_workspace(request, workspace_id):
    """Menja aktivni workspace."""
    manager = GraphManager()
    try:
        manager.switch_workspace(workspace_id)
        return JsonResponse({"status": "ok", "active_id": workspace_id})
    except ValueError as e:
        return JsonResponse({"error": str(e)}, status=404)

def api_delete_workspace(request, workspace_id):
    """Brise workspace."""
    manager = GraphManager()
    manager.delete_workspace(workspace_id)
    return JsonResponse({"status": "ok"})

def api_visualize(request, graph_id):
    """
    Vraća HTML vizualizaciju. graph_id je UUID workspace-a.
    """
    visualizer_name = request.GET.get('visualizer')
    manager = GraphManager()
    
    # 1. Pronađi workspace u menadžeru
    workspace = manager.workspace_manager.get_workspace(graph_id)
    
    if not workspace:
         return HttpResponseNotFound(f"Workspace {graph_id} nije pronađen (Možda je server restartovan?).")
    
    # 2. Postavi ga kao aktivnog da bi render metoda znala šta da crta
    manager.switch_workspace(graph_id)

    if not visualizer_name:
        visualizer_name = workspace.selected_visualizer
    if not visualizer_name:
        return HttpResponse("Please select a visualizer", status=400)
    
    workspace.selected_visualizer = visualizer_name
    
    try:
        vis_loader = VisualizerLoader()
        
        # Ponovna registracija za svaki slučaj (u produkciji bi ovo bilo u __init__)
        try:
            from simple_visualizer.simple_visualizer.plugin import SimpleVisualizer
            vis_loader.register_visualizer(SimpleVisualizer().name(), SimpleVisualizer)
        except ImportError: pass

        try:
            from block_visualizer.block_visualizer.plugin import BlockVisualizer
            vis_loader.register_visualizer(BlockVisualizer().name(), BlockVisualizer)
        except ImportError: pass
        
        vis_instance = vis_loader.get_visualizer(visualizer_name)
        manager.set_visualizer(vis_instance)
        
        # Renderuj AKTIVNI graf
        return HttpResponse(manager.render())
        
    except Exception as e:
        import traceback
        traceback.print_exc() 
        return HttpResponse(f"Greska pri renderovanju: {str(e)}", status=500)

def api_graph_json(request, graph_id):
    """
    Vraća JSON strukturu za Tree View na osnovu Workspace ID-a.
    """
    manager = GraphManager()
    
    # Trazimo workspace po ID-ju
    workspace = manager.workspace_manager.get_workspace(graph_id)

    if not workspace:
        return HttpResponseNotFound(f"Workspace sa ID {graph_id} nije pronađen.")
    
    # Uzimamo trenutni graf iz workspace-a
    graph = workspace.current_graph
    
    nodes = []
    for n in graph.nodes:
        label = getattr(n, "label", str(n.id)) or str(n.id)
        nodes.append({"id": str(n.id), "label": label})
        
    links = []
    for e in graph.edges:
        s = e.source.id if hasattr(e.source, "id") else e.source
        t = e.target.id if hasattr(e.target, "id") else e.target
        links.append({"source": str(s), "target": str(t)})
        
    return JsonResponse({"nodes": nodes, "links": links})

def api_search(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    
    manager = GraphManager()
    try:
        data = json.loads(request.body)
        query = data.get("query", "").strip()

        if not manager.workspace_manager.get_active_workspace():
             return JsonResponse({"error": "No active workspace"}, status=400)

        result_graph = manager.apply_search(query)
        return JsonResponse(result_graph.to_dict(), safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def api_filter(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    
    manager = GraphManager()
    try:
        data = json.loads(request.body)
        attribute = data.get("attribute")
        operator = data.get("operator")
        value = data.get("value")

        if not manager.workspace_manager.get_active_workspace():
             return JsonResponse({"error": "No active workspace"}, status=400)

        result_graph = manager.apply_filter(attribute, operator, value)
        return JsonResponse(result_graph.to_dict(), safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def api_reset(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    manager = GraphManager()
    try:
        if not manager.workspace_manager.get_active_workspace():
             return JsonResponse({"error": "No active workspace"}, status=400)

        result_graph = manager.reset_graph()
        return JsonResponse(result_graph.to_dict(), safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)