from django.apps import AppConfig


class AppCarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_car'

    def ready(self):
        import app_car.signals
