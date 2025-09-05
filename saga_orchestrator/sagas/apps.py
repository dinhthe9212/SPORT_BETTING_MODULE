from django.apps import AppConfig

class SagasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'sagas'
    
    def ready(self):
        # Import signal handlers if any
        pass

