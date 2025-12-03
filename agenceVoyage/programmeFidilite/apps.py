from django.apps import AppConfig


class ProgrammefidiliteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'programmeFidilite'
    
    def ready(self):
        import programmeFidilite.signals
