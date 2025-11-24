import os
from django.shortcuts import render
from django.views import View
from django.conf import settings
from pathlib import Path
from graph_platform.platform.graph_manager import GraphManager

class IndexView(View):
    def get(self, request):
        # Inicijalizacija Loadera
        manager = GraphManager()
        loader = manager.get_data_source_loader()

        known_plugins = ["data_source_json.data_source_json", "data_source_csv.data_source_csv"]
        loader.load_plugins(known_plugins)
        
        # dobijanje liste pluginova
        plugins = loader.get_available_plugins()
        
        # 3. Automatsko skeniranje fajlova za svaki plugin
        # Ovo mapira: "JSON Data Source" -> ["file1.json", "file2.json"]
        files_map = {}
        
        base_dir = Path(__file__).resolve().parent.parent.parent.parent # graph-visualizer root
        
        # Mapiranje imena plugina na folder sa podacima (Hardcoded za sada, jer plugin API nema metodu za ovo)
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
                            # puna putanja - vrednost, ime fajla - prikaz
                            full_path = os.path.join(folder_path, file)
                            files_map[plugin_name].append({
                                'name': file,
                                'path': full_path
                            })
                except Exception as e:
                    print(f"Greška pri čitanju foldera {folder_path}: {e}")

        # slanje podataka u template
        context = {
            "plugins": plugins,
            "files_map": files_map, #saljemo mapu fajlova
        }
        return render(request, "core/index.html", context)

    def post(self, request):
        # kad se klikne Load, ostajemo na istoj strani
        # bice logika za GraphManager
        return self.get(request)