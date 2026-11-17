from django.apps import AppConfig


class PolicialConfig(AppConfig):
    name = 'policial'

    def ready(self):
        import policial.signals