"""
WebSocket URL routing for Carousel Service
Cost: $0 (Django Channels routing)
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Main carousel WebSocket
    re_path(r'ws/carousel/$', consumers.CarouselConsumer.as_asgi()),
    
    # Stats WebSocket (admin only)
    re_path(r'ws/carousel/stats/$', consumers.CarouselStatsConsumer.as_asgi()),
]
