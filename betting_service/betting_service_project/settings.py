import sys
from pathlib import Path
import os
from decouple import config

# Add parent directory to Python path to access shared module
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from shared.base_settings import *

SERVICE_NAME = 'betting_service'
SERVICE_PORT = 8002
SERVICE_VERSION = '1.0.0'

INSTALLED_APPS += [
    'betting.apps.BettingConfig',
    'django_prometheus',
    'drf_spectacular',
]

# Database configuration for Betting Service
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='betting_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres123'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# Redis configuration for Betting Service
REDIS_DB = 2  # Use a different DB for each service
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# Logging for Betting Service
LOGGING['handlers']['file']['filename'] = BASE_DIR / 'logs' / 'betting_service.log'
LOGGING['loggers']['betting'] = {
    'handlers': ['console', 'file'],
    'level': 'DEBUG',
    'propagate': False,
}

# Add service name to log formatters
LOGGING['formatters']['json']['format'] = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "betting_service", "module": "%(module)s", "message": "%(message)s"}'


# HTTPS/TLS Settings (only for production)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Service URLs
RISK_SERVICE_URL = config('RISK_SERVICE_URL', default='http://risk-management-service:8003')
WALLET_SERVICE_URL = config('WALLET_SERVICE_URL', default='http://wallet-service:8004')
SAGA_SERVICE_URL = config('SAGA_SERVICE_URL', default='http://saga-orchestrator:8008')
SPORTS_SERVICE_URL = config('SPORTS_SERVICE_URL', default='http://sports-data-service:8005')

# Internal API Keys for service-to-service communication
INTERNAL_API_KEYS = [
    config('BETTING_API_KEY', default='dev-betting-key-123'),
    config('INTERNAL_API_KEY', default='dev-internal-key-456'),
]

# Rate Limiting Settings
RATE_LIMIT_MAX_REQUESTS = config('RATE_LIMIT_MAX_REQUESTS', default=100, cast=int)
RATE_LIMIT_WINDOW = config('RATE_LIMIT_WINDOW', default=60, cast=int)

# Betting Service Specific Settings
MAX_BET_AMOUNT = config('MAX_BET_AMOUNT', default=10000, cast=float)
MIN_BET_AMOUNT = config('MIN_BET_AMOUNT', default=1, cast=float)
MAX_ODDS = config('MAX_ODDS', default=1000, cast=float)
MIN_ODDS = config('MIN_ODDS', default=1.01, cast=float)

# Auto Order Management Settings
AUTO_ORDER_ENABLED = config('AUTO_ORDER_ENABLED', default=True, cast=bool)
AUTO_ORDER_TIMEOUT = config('AUTO_ORDER_TIMEOUT', default=300, cast=int)  # 5 minutes

# Cash Out Settings
CASHOUT_ENABLED = config('CASHOUT_ENABLED', default=True, cast=bool)
CASHOUT_MIN_AMOUNT = config('CASHOUT_MIN_AMOUNT', default=10, cast=float)
CASHOUT_MAX_AMOUNT = config('CASHOUT_MAX_AMOUNT', default=5000, cast=float)

# API Documentation Settings
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Betting Service API',
    'DESCRIPTION': 'API documentation for the Betting Service microservice. This service handles all P2P betting activities including odds management, bet placement, cash out, P2P marketplace, and fractional ownership.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/betting/',
    'TAGS': [
        {'name': 'Sports', 'description': 'Sports management endpoints'},
        {'name': 'Teams', 'description': 'Teams management endpoints'},
        {'name': 'Matches', 'description': 'Matches management endpoints'},
        {'name': 'Bet Types', 'description': 'Bet types management endpoints'},
        {'name': 'Odds', 'description': 'Odds management and analytics endpoints'},
        {'name': 'Bet Slips', 'description': 'Bet slips management endpoints'},
        {'name': 'Bet Selections', 'description': 'Bet selections management endpoints'},
        {'name': 'Bet Slip Purchases', 'description': 'Bet slip purchases management endpoints'},
        {'name': 'Cash Out', 'description': 'Cash out operations and configuration'},
        {'name': 'P2P Marketplace', 'description': 'P2P marketplace and fractional ownership'},
        {'name': 'Auto Orders', 'description': 'Automatic order management (Take Profit & Stop Loss)'},
        {'name': 'Market Suspension', 'description': 'Market suspension management'},
        {'name': 'Statistics', 'description': 'Statistics and leaderboard endpoints'},
        {'name': 'Responsible Gaming', 'description': 'Responsible gaming policies and activity logs'},
    ],
}


