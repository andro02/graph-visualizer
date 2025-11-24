import os
from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from django.contrib import messages
from pathlib import Path
from graph_platform.platform.graph_manager import GraphManager
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound

class IndexView(View):
    def _get_context_data(self):
        """Pomoćna metoda koja priprema podatke za dropdown menije."""
        manager = GraphManager()
        loader = manager.get_data_source_loader()
        
        # ucitavanje poznatih plugina
        known_plugins = ["data_source_json.data_source_json", "data_source_csv.data_source_csv"]
        loader.load_plugins(known_plugins)
        
        plugins = loader.get_available_plugins()
        
        # skeniranje fajlova
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
                except Exception as e:
                    print(f"Greska pri citanju foldera {folder_path}: {e}")

        return {
            "plugins": plugins,
            "files_map": files_map,
        }

    def get(self, request):
        # Prikazuje praznu formu (resetovanu)
        context = self._get_context_data()
        return render(request, "core/index.html", context)

    def post(self, request):
        plugin_name = request.POST.get('plugin_name')
        file_path = request.POST.get('source_path')

        if not plugin_name or not file_path:
            messages.error(request, "Morate izabrati plugin i fajl!")
            return self.get(request)

        manager = GraphManager()
        try:
            # Učitavamo graf i smeštamo u keš
            # Šaljemo "path" parametar (CSV plugin mora biti podešen da ovo prihvata)
            graph = manager.load_graph_from_source(plugin_name, {"path": file_path})
            
            messages.success(request, f"Graf uspešno učitan! ({len(graph.nodes)} čvorova, {len(graph.edges)} veza)")
        except Exception as e:
            messages.error(request, f"Greška pri učitavanju: {str(e)}")
        
        # resetuje select polja na pocetno stanje
        return self.get(request)
    
def api_graphs(request):
    """
    Vraca listu ID-jeva ucitanih grafova iz kesa.
    """
    manager = GraphManager()
    # Vraćamo ključeve iz keša (ID grafova)
    loaded_graphs = list(manager._cache.keys())
    return JsonResponse({"graphs": loaded_graphs})

def api_visualize(request, graph_id):
    """
    Vraca HTML vizualizaciju za zadati graph_id.
    """
    manager = GraphManager()
    
    #Provera da li graf postoji u kesu
    # graph_id da se poklapa sa kljucem u manager._cache)
    if graph_id not in manager._cache:
        return HttpResponseNotFound(f"Graf '{graph_id}' nije pronadjen u memoriji.")
    
    graph = manager._cache[graph_id]
    
    # Biramo vizualizer
    try:
        from block_visualizer.block_visualizer.plugin import BlockVisualizer
        manager.set_visualizer(BlockVisualizer())
        
        # renderovanje
        html_output = manager.render(graph)
        return HttpResponse(html_output)
    except ImportError:
        return HttpResponse("BlockVisualizer nije instaliran.", status=500)
    except Exception as e:
        return HttpResponse(f"Greska pri renderovanju: {str(e)}", status=500)