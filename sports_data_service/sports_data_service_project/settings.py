import sys
from pathlib import Path
from decouple import config

# Add parent directory to Python path to access shared module
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from shared.base_settings import *

SERVICE_NAME = 'sports_data_service'
SERVICE_PORT = 8005
SERVICE_VERSION = '1.0.0'

INSTALLED_APPS += [
    'sports_data',
    'drf_spectacular',
    'django_celery_beat',
    'django_celery_results',
]

# Database configuration for Sports Data Service
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='sports_data_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres123'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# Redis configuration for Sports Data Service
REDIS_DB = 5  # Use a different DB for each service
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# Logging for Sports Data Service
LOGGING['handlers']['file']['filename'] = BASE_DIR / 'logs' / 'sports_data_service.log'
LOGGING['loggers']['sports_data'] = {
    'handlers': ['console', 'file'],
    'level': 'DEBUG',
    'propagate': False,
}

# Add service name to log formatters
LOGGING['formatters']['json']['format'] = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "sports_data_service", "module": "%(module)s", "message": "%(message)s"}'

# Sports Data Service Specific Settings
API_SPORTS_KEY = config('API_SPORTS_KEY', default='')
THE_ODDS_API_KEY = config('THE_ODDS_API_KEY', default='')
OPENLIGADB_KEY = config('OPENLIGADB_KEY', default='')
THESPORTSDB_KEY = config('THESPORTSDB_KEY', default='')

# JWT Configuration
JWT_SECRET_KEY = config('JWT_SECRET_KEY', default='your-super-secret-jwt-key-change-in-production')
JWT_ALGORITHM = config('JWT_ALGORITHM', default='HS256')
JWT_ACCESS_TOKEN_EXPIRY = config('JWT_ACCESS_TOKEN_EXPIRY', default=15, cast=int)
JWT_REFRESH_TOKEN_EXPIRY = config('JWT_REFRESH_TOKEN_EXPIRY', default=7, cast=int)

# Alerting Configuration
ALERT_EMAIL_HOST = config('ALERT_EMAIL_HOST', default='smtp.gmail.com')
ALERT_EMAIL_PORT = config('ALERT_EMAIL_PORT', default=587, cast=int)
ALERT_EMAIL_USER = config('ALERT_EMAIL_USER', default='')
ALERT_EMAIL_PASSWORD = config('ALERT_EMAIL_PASSWORD', default='')
ALERT_SLACK_WEBHOOK_URL = config('ALERT_SLACK_WEBHOOK_URL', default='')

# Circuit Breaker Settings
CIRCUIT_BREAKER_SETTINGS = {
    'failure_threshold': config('CIRCUIT_BREAKER_FAILURE_THRESHOLD', default=3, cast=int),
    'recovery_timeout': config('CIRCUIT_BREAKER_RECOVERY_TIMEOUT', default=120, cast=int),
    'expected_exception': Exception
}

# Cache Strategy
CACHE_SETTINGS = {
    'live_scores_ttl': config('CACHE_LIVE_SCORES_TTL', default=60, cast=int),
    'fixtures_ttl': config('CACHE_FIXTURES_TTL', default=3600, cast=int),
    'odds_data_ttl': config('CACHE_ODDS_DATA_TTL', default=300, cast=int),
    'provider_metrics_ttl': config('CACHE_PROVIDER_METRICS_TTL', default=1800, cast=int)
}

# Alerting Rules
ALERT_RULES = {
    'data_sync_failure': {
        'cooldown': config('ALERT_DATA_SYNC_COOLDOWN', default=300, cast=int),
        'max_alerts_per_hour': config('ALERT_DATA_SYNC_MAX_PER_HOUR', default=3, cast=int)
    },
    'provider_down': {
        'cooldown': config('ALERT_PROVIDER_DOWN_COOLDOWN', default=600, cast=int),
        'max_alerts_per_hour': config('ALERT_PROVIDER_DOWN_MAX_PER_HOUR', default=2, cast=int)
    }
}

# Internal API Keys
INTERNAL_API_KEYS = [
    config('SPORTS_API_KEY', default='dev-sports-key-123'),
    config('INTERNAL_API_KEY', default='dev-internal-key-456'),
]

# Rate Limiting Settings
RATE_LIMIT_MAX_REQUESTS = config('RATE_LIMIT_MAX_REQUESTS', default=100, cast=int)
RATE_LIMIT_WINDOW = config('RATE_LIMIT_WINDOW', default=60, cast=int)

# API Documentation Settings
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Sports Data Service API',
    'DESCRIPTION': 'API documentation for the Sports Data Service microservice. This service provides comprehensive sports data from multiple providers with real-time synchronization, data validation, and advanced monitoring.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
    'TAGS': [
        {'name': 'Live Scores', 'description': 'Real-time live scores and match data'},
        {'name': 'Fixtures', 'description': 'Match fixtures and scheduling'},
        {'name': 'Odds Data', 'description': 'Betting odds from multiple providers'},
        {'name': 'Data Synchronization', 'description': 'Data sync and validation endpoints'},
        {'name': 'Provider Management', 'description': 'External API provider management'},
        {'name': 'Health Check', 'description': 'Service health and status endpoints'},
    ],
}

# Celery Configuration for Cron Jobs
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_TIMEZONE = 'UTC'
CELERY_ENABLE_UTC = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
CELERY_CACHE_BACKEND = 'django-cache'
