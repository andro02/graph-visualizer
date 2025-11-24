import os
import base64
import inspect
from pathlib import Path
from django.shortcuts import render
from django.views import View
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
from graph_platform.platform.graph_manager import GraphManager
from graph_platform.platform.visualizer_loader import VisualizerLoader

class IndexView(View):
    def _get_context_data(self, selected_visualizer=None):
        """Priprema podatke za dropdown menije."""
        manager = GraphManager()
        loader = manager.get_data_source_loader()

        vis_loader = VisualizerLoader()
        vis_loader = VisualizerLoader()
        
        # Ručno uvozimo i registrujemo vizualizere da budemo 100% sigurni
        try:
            from simple_visualizer.simple_visualizer.plugin import SimpleVisualizer
            vis_loader.register_visualizer(SimpleVisualizer().name(), SimpleVisualizer)
        except ImportError as e:
            print(f"Greška pri učitavanju SimpleVisualizer: {e}")

        try:
            from block_visualizer.block_visualizer.plugin import BlockVisualizer
            vis_loader.register_visualizer(BlockVisualizer().name(), BlockVisualizer)
        except ImportError as e:
            print(f"Greška pri učitavanju BlockVisualizer: {e}")
            
        visualizers = vis_loader.list_visualizers()
        
        # Učitavanje pluginova
        known_plugins = ["data_source_json.data_source_json", "data_source_csv.data_source_csv"]
        loader.load_plugins(known_plugins)
        
        plugins = loader.get_available_plugins()
        
        # Skeniranje fajlova
        files_map = {}
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
        
        # 1. Hvatamo šta je korisnik izabrao za vizualizer
        visualizer = request.POST.get('visualizer') 

        if not plugin_name or not file_path:
            messages.error(request, "Morate izabrati plugin i fajl!")
            # Vraćamo i vizualizer da se ne resetuje
            context = self._get_context_data(selected_visualizer=visualizer)
            return render(request, "core/index.html", context)

        manager = GraphManager()
        try:
            graph = manager.load_graph_from_source(plugin_name, {"path": file_path})
            
            graph_id = f"{plugin_name}_{file_path}"
            raw_cache_key = f"{plugin_name}_{file_path}"
            graph_id_safe = base64.urlsafe_b64encode(raw_cache_key.encode()).decode()
            
            messages.success(request, f"Graf uspešno učitan! ({len(graph.nodes)} čvorova)")
            
            # 2. Šaljemo visualizer nazad u kontekst
            context = self._get_context_data(selected_visualizer=visualizer)
            context['graph_id'] = graph_id_safe
            
            return render(request, "core/index.html", context)
            
        except Exception as e:
            messages.error(request, f"Greška pri učitavanju: {str(e)}")
        
        # I ovde vraćamo vizualizer
        context = self._get_context_data(selected_visualizer=visualizer)
        return render(request, "core/index.html", context)

# --- API Funkcije ostaju iste ---
def api_graphs(request):
    manager = GraphManager()
    loaded_graphs = list(manager._cache.keys())
    return JsonResponse({"graphs": loaded_graphs})

def api_visualize(request, graph_id):
    """Vraća HTML vizualizaciju za zadati graph_id."""
    visualizer_name = request.GET.get('visualizer')
    manager = GraphManager()
    
    try:
        # 1. Dekodiramo ID
        decoded_key = base64.urlsafe_b64decode(graph_id).decode()
    except Exception:
        return HttpResponseNotFound("Nevalidan ID grafa.")

    # 2. Proveravamo keš
    if decoded_key not in manager._cache:
        return HttpResponseNotFound(f"Graf nije pronadjen.")
    
    graph = manager._cache[decoded_key]

    # Dinamičko učitavanje vizualizera
    if not visualizer_name:
        return HttpResponse("Please select a visualizer", status=400)
    
    # 3. Renderujemo
    try:
        vis_loader = VisualizerLoader()
        
        # Ponovo registrujemo da bismo ih našli
        from simple_visualizer.simple_visualizer.plugin import SimpleVisualizer
        vis_loader.register_visualizer(SimpleVisualizer().name(), SimpleVisualizer)
        
        from block_visualizer.block_visualizer.plugin import BlockVisualizer
        print(f"👀 GDE JE BLOCK? -> {inspect.getfile(BlockVisualizer)}")
        
        # Provera da li smo slučajno uvezli SimpleVisualizer pod imenom BlockVisualizer
        dummy_instance = BlockVisualizer()
        print(f"👀 KAKO SE ZOVE? -> {dummy_instance.name()}")
        print(f"👀 ŠTA JE OVO? -> {type(dummy_instance)}")
        
        vis_loader.register_visualizer(BlockVisualizer().name(), BlockVisualizer)
        # --------------------------------
        
        vis_instance = vis_loader.get_visualizer(visualizer_name)
        
        manager.set_visualizer(vis_instance)
        return HttpResponse(manager.render(graph))
        
    except KeyError:
        return HttpResponse(f"Visualizer '{visualizer_name}' not found.", status=404)
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)