"""
Django settings for carousel_service_project project.
"""

import sys
from pathlib import Path
from decouple import config

# Add parent directory to Python path to access shared module
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from shared.base_settings import *

SERVICE_NAME = 'carousel_service'
SERVICE_PORT = 8006
SERVICE_VERSION = '1.0.0'


# Application definition
INSTALLED_APPS += [
    'carousel',
    'channels',  # WebSocket support
]

# Add custom middleware
MIDDLEWARE.insert(1, 'carousel.optimizations.PerformanceMiddleware')

# Import shared security middleware 
try:
    from shared.middleware import RateLimitMiddleware, SecurityHeadersMiddleware, APIKeyAuthMiddleware
    MIDDLEWARE.insert(-1, 'shared.middleware.RateLimitMiddleware')
    MIDDLEWARE.insert(-1, 'shared.middleware.SecurityHeadersMiddleware')
    MIDDLEWARE.insert(-1, 'shared.middleware.APIKeyAuthMiddleware')
except ImportError:
    print("Warning: Security middleware not found. Using basic security only.")

ROOT_URLCONF = 'carousel_service_project.urls'

# Database configuration for Carousel Service
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='carousel_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres123'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# Redis configuration for Carousel Service
REDIS_DB = 6  # Use a different DB for each service
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# Cache settings
CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 300  # 5 minutes
CACHE_MIDDLEWARE_KEY_PREFIX = 'carousel_service'


# Logging for Carousel Service
LOGGING['handlers']['file']['filename'] = BASE_DIR / 'logs' / 'carousel_service.log'
LOGGING['loggers']['carousel'] = {
    'handlers': ['console', 'file'],
    'level': 'DEBUG',
    'propagate': False,
}

# Add service name to log formatters
LOGGING['formatters']['json']['format'] = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "carousel_service", "module": "%(module)s", "message": "%(message)s"}'

# ASGI Application for WebSocket support
ASGI_APPLICATION = 'carousel_service_project.asgi.application'

# Channel Layer Configuration (Redis-based for WebSocket)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'],
            "capacity": 300,  # Maximum messages to store in a channel
            "expiry": 60,     # Seconds until a message expires
        },
    },
    # Fallback for development without Redis
    'inmemory': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    }
}

# Carousel Service Specific Settings
RATE_LIMIT_ENABLED = config('RATE_LIMIT_ENABLED', default=True, cast=bool)
MAX_DAILY_PURCHASES_PER_USER = config('MAX_DAILY_PURCHASES_PER_USER', default=20, cast=int)

# Internal API Keys for service-to-service communication
INTERNAL_API_KEYS = [
    config('CAROUSEL_API_KEY', default='dev-carousel-key-123'),
    config('GROUPS_API_KEY', default='dev-groups-key-456'),
]

# Rate Limiting Settings
RATE_LIMIT_MAX_REQUESTS = config('RATE_LIMIT_MAX_REQUESTS', default=100, cast=int)
RATE_LIMIT_WINDOW = config('RATE_LIMIT_WINDOW', default=60, cast=int)

# Performance Optimization Settings
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Cloudflare CDN Integration
CLOUDFLARE_ENABLED = config('CLOUDFLARE_ENABLED', default=False, cast=bool)
CLOUDFLARE_API_TOKEN = config('CLOUDFLARE_API_TOKEN', default='')
CLOUDFLARE_ZONE_ID = config('CLOUDFLARE_ZONE_ID', default='')

# Custom cache headers for CDN
CLOUDFLARE_CACHE_HEADERS = {
    'static_files': {
        'Cache-Control': 'public, max-age=86400',  # 1 day
        'CF-Cache-Tag': 'static'
    },
    'api_responses': {
        'Cache-Control': 'public, max-age=300',    # 5 minutes
        'CF-Cache-Tag': 'api'
    },
    'analytics': {
        'Cache-Control': 'public, max-age=900',    # 15 minutes
        'CF-Cache-Tag': 'analytics'
    }
}
