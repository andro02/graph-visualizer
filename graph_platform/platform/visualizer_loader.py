import importlib
import pkgutil
from typing import Dict, Type
from api.api.base_visualizer import BaseVisualizer


class VisualizerLoader:
    def __init__(self):
        self._registry: Dict[str, Type[BaseVisualizer]] = {}

    def load_visualizers(self, package: str):
        """
        Učitava sve vizualizere iz prosleđenog Python paketa.
        """
        discovered = pkgutil.iter_modules([package])

        for module_info in discovered:
            module_name = module_info.name
            full_path = f"{package}.{module_name}"

            module = importlib.import_module(full_path)

            # Traži sve klase u modulu
            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                # Mora biti klasa i mora nasleđivati BaseVisualizer
                if isinstance(attr, type) and issubclass(attr, BaseVisualizer) and attr is not BaseVisualizer:
                    self.register_visualizer(attr_name, attr)

    def register_visualizer(self, name: str, cls: Type[BaseVisualizer]):
        """
        Registruje vizualizer po imenu.
        """
        if not issubclass(cls, BaseVisualizer):
            raise TypeError(f"Visualizer '{name}' ne nasleđuje BaseVisualizer.")

        self._registry[name] = cls

    def get_visualizer(self, name: str) -> BaseVisualizer:
        """
        Instancira vizualizer.
        """
        if name not in self._registry:
            raise KeyError(f"Visualizer '{name}' nije registrovan.")

        return self._registry[name]()

    def list_visualizers(self):
        """
        Vraća listu registrovanih vizualizera.
        """
        return list(self._registry.keys())
