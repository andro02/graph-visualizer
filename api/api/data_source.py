from abc import ABC, abstractmethod
from typing import Any, List, Dict
from enum import Enum
from .graph import Graph 

#dodajemo model za opis ulaznog parametra
#korisno jer moramo reći platformi koji tip ulaza očekujemo (fajl, tekst, url)
class PluginParameterType(Enum):
    """
    Tip parametra kako bi UI znao šta da iscrta.
    Na osnovu specifikacije (2.2):
    - "putanja do fajla" -> FILE
    - "API_URL", "API_KEY" -> TEXT
    - Brojčane vrednosti -> INTEGER/FLOAT
    """
    TEXT = "text"
    FILE = "file"
    INTEGER = "integer"
    BOOLEAN = "boolean"

class PluginParameter:
    def __init__(self, name: str, description: str, type: PluginParameterType = PluginParameterType.TEXT, is_required: bool = True, default_value: Any = None):
        self.name = name
        self.description = description
        self.type = type
        self.is_required = is_required
        self.default_value = default_value

class DataSourcePlugin(ABC):
    """
    Apstraktna bazna klasa za sve Data Source plugin-ove.
    Definiše ugovor koji svaki plugin mora da poštuje.
    """

    @abstractmethod
    def name(self) -> str:
        """
        Vraća naziv plugin-a koji će biti prikazan korisniku.
        Primer: "CSV Data Source"
        """
        pass
        
    @abstractmethod
    def get_parameters(self) -> List[PluginParameter]:
        """Vraća listu ulaznih parametara koje plugin očekuje od korisnika."""
        pass

    @abstractmethod
    def parse(self, parameters: Dict[str, Any]) -> Graph:
        """
        Glavna metoda za parsiranje podataka.

        Args:
            parameters (Dict[str, Any]): Rečnik (dictionary) sa ključevima 
                                         i vrednostima koje je definisao korisnik 
                                         preko get_parameters().
            
        Returns:
            Graph: Instanciran i popunjen objekat grafa.
        """
        pass