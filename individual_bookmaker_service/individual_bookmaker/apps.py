from django.apps import AppConfig


class IndividualBookmakerConfig(AppConfig):
    """Configuration cho Individual Bookmaker app"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'individual_bookmaker'
    verbose_name = 'Individual Bookmaker Service'
    
    def ready(self):
        """Được gọi khi app được load"""
        try:
            import individual_bookmaker.signals  # noqa
        except ImportError:
            pass
