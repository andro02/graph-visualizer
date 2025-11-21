import unittest
from unittest import mock
from typing import Dict, Any, List
from api.api.data_source import DataSourcePlugin, PluginParameter, PluginParameterType
from api.api.graph import Graph
from platform.platform.data_source_loader import DataSourceLoader

class DummyCsvPlugin(DataSourcePlugin):
    """Konkretna klasa koja implementira API ugovor za testiranje loadera."""
    def name(self) -> str:
        return "Dummy CSV Source"
    def get_parameters(self) -> List[PluginParameter]:
        return [PluginParameter(name='path', description='File path')]
    def parse(self, parameters: Dict[str, Any]) -> Graph:
        return Graph()

class DummyJsonPlugin(DataSourcePlugin):
    """Drugi konkretan plugin za testiranje visestruke registracije."""
    def name(self) -> str:
        return "Dummy JSON Source"
    def get_parameters(self) -> List[PluginParameter]:
        return [PluginParameter(name='url', description='API URL')]
    def parse(self, parameters: Dict[str, Any]) -> Graph:
        return Graph()


class TestDataSourceLoader(unittest.TestCase):

    def setUp(self):
        """Postavljanje novog loadera pre svakog testa."""
        self.loader = DataSourceLoader()

    def test_initial_state(self):
        """Proverava da li je registar u pocetku prazan."""
        self.assertEqual(self.loader.get_available_plugins(), [])
        
    def test_manual_registration(self):
        """Proverava rucnu registraciju ispravnog plugina."""
        self.loader.register_plugin(DummyCsvPlugin)
        self.assertIn("Dummy CSV Source", self.loader.get_available_plugins())
        
        # Proveravamo da li je instanca ispravnog tipa
        plugin_instance = self.loader.get_plugin("Dummy CSV Source")
        self.assertIsInstance(plugin_instance, DummyCsvPlugin)
        self.assertIsInstance(plugin_instance, DataSourcePlugin)

    def test_registration_name_conflict(self):
        """Proverava da li loader upozorava i ignoriše duple registracije."""
        self.loader.register_plugin(DummyCsvPlugin)
        
        # Pokusavamo da registrujemo ponovo
        with self.assertLogs(level='WARNING') as cm:
             self.loader.register_plugin(DummyCsvPlugin)
        
        # Provera da li je u registru ostao samo jedan plugin
        self.assertEqual(len(self.loader.get_available_plugins()), 1)
        self.assertEqual(len(self.loader._registry), 1)

    @mock.patch('importlib.import_module')
    def test_dynamic_loading_success(self, mock_import):
        """
        Simulira dinamicko ucitavanje dva plugina iz fiktivnog paketa.
        """
        mock_module = mock.MagicMock()
        mock_module.DummyCsvPlugin = DummyCsvPlugin
        mock_module.DummyJsonPlugin = DummyJsonPlugin
        
        #definise se sta import_module vraca
        mock_import.return_value = mock_module
        
        #definise se sta dir(module) vraca simuliranog direktorijuma modula ()
        def fake_dir(obj):
            if obj == mock_module:
                # Simuliramo da su ove klase prisutne
                return ['DummyCsvPlugin', 'DummyJsonPlugin', 'NekiDrugiObjekat']
            return unittest.mock.DEFAULT

        #izvrsavanje loadera
        with mock.patch('builtins.dir', side_effect=fake_dir):
            #uciitavamo fiktivni paket
            self.loader.load_plugins(['data_source_plugins_parent']) 

        self.assertIn('Dummy CSV Source', self.loader.get_available_plugins())
        self.assertIn('Dummy JSON Source', self.loader.get_available_plugins())
        self.assertEqual(len(self.loader.get_available_plugins()), 2)
        
    @mock.patch('importlib.import_module', side_effect=ImportError)
    def test_loading_plugin_import_error(self, mock_import):
        """
        Proverava da li loader ne puca ako ne može da uveze neki paket.
        """
        # Loadere pokusava da uveze paket koji izaziva ImportError
        self.loader.load_plugins(['nepostojeci_paket'])
        
        self.assertEqual(self.loader.get_available_plugins(), [])


if __name__ == '__main__':
    unittest.main()