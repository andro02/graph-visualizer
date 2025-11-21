from typing import Dict, Type, List
from api.api.data_source import DataSourcePlugin

class DataSourceLoader:
    def __init__(self):
        # Registar čuva mapiranje: "Naziv Plugina" -> Klasa Plugina
        self._registry: Dict[str, Type[DataSourcePlugin]] = {}

    def get_available_plugins(self) -> List[str]:
        """
        Vraca listu naziva svih registrovanih plugina.
        """
        return list(self._registry.keys())

    def get_plugin(self, name: str) -> DataSourcePlugin:
        """
        Vraca novu instancu trazenog plugina.
        """
        if name not in self._registry:
            raise KeyError(f"Data Source plugin '{name}' nije pronadjen.")
        
        return self._registry[name]()