import importlib
from typing import Dict, Type, List
from api.api.data_source import DataSourcePlugin
import logging
logger = logging.getLogger(__name__)

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
                logger.warning(f"Plugin sa imenom '{name}' je već registrovan. Preskačem.")
                return

            self._registry[name] = cls
            logger.info(f"Uspešno registrovan Data Source plugin: {name}")
            
        except Exception as e:
            print(f"Gresaka pri registraciji plugina {cls}: {e}")

    def load_plugins(self, packages: List[str]):
        """
        Ucitava plugine iz liste navedenih paketa.
        Args:
            packages: Lista naziva paketa (npr. ['data_source_csv', 'data_source_json'])
        """
        for package in packages:
            try:
                module = importlib.import_module(package)
                # Prolazimo kroz sve atribute u modulu
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    
                    # Provera: Da li je klasa, da li nasleđuje API, i da nije sama API klasa
                    if (isinstance(attr, type) and 
                        issubclass(attr, DataSourcePlugin) and 
                        attr is not DataSourcePlugin):
                        
                        self.register_plugin(attr)
            except ImportError as e:
                print(f"Nije moguce ucitati plugin paket '{package}': {e}")