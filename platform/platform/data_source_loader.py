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
    
    def register_plugin(self, cls: Type[DataSourcePlugin]):
        """
        Registruje klasu plugina u interni registar.
        """
        try:
            # Instanciramo plugin da bismo dobili njegovo ime
            instance = cls()
            name = instance.name()
            
            if name in self._registry:
                print(f"Upozorenje: Plugin '{name}' je već registrovan.")
                return

            self._registry[name] = cls
            print(f"Registrovan plugin: {name}")
            
        except Exception as e:
            print(f"Greška pri registraciji plugina {cls}: {e}")