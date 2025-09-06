"""
ASGI config for Individual Bookmaker Service.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'individual_bookmaker_service.settings')

application = get_asgi_application()
