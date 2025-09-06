"""
ASGI config for carousel_service_project project.
WebSocket support with Django Channels
Cost: $0 (Django Channels is free)
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import carousel.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carousel_service_project.settings')

application = ProtocolTypeRouter({
    # HTTP requests
    "http": get_asgi_application(),
    
    # WebSocket requests
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                carousel.routing.websocket_urlpatterns
            )
        )
    ),
})