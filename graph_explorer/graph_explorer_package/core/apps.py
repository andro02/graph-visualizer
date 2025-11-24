from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        # importujemo i inicijalizujemo platformu kad se Django digne
        from graph_platform.platform.graph_manager import GraphManager
        GraphManager() # inicijalizacija managera
