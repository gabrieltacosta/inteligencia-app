from django.apps import AppConfig


class MaterialConfig(AppConfig):
    name = 'material'

    def ready(self):
        import material.signals  # Importa os sinais para garantir que eles sejam registrados