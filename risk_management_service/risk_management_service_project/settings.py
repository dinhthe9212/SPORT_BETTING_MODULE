import sys
from pathlib import Path
from decouple import config

# Add parent directory to Python path to access shared module
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from shared.base_settings import *

SERVICE_NAME = 'risk_management_service'
SERVICE_PORT = 8003
SERVICE_VERSION = '1.0.0'

# Application definition
INSTALLED_APPS += [
    'risk_manager',
    'drf_spectacular',
]

ROOT_URLCONF = 'risk_management_service_project.urls'

# Database configuration for Risk Management Service
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='risk_management_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres123'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# Redis configuration for Risk Management Service
REDIS_DB = 3  # Use a different DB for each service
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# Logging for Risk Management Service
LOGGING['handlers']['file']['filename'] = BASE_DIR / 'logs' / 'risk_management_service.log'
LOGGING['loggers']['risk_manager'] = {
    'handlers': ['console', 'file'],
    'level': 'DEBUG',
    'propagate': False,
}

# Add service name to log formatters
LOGGING['formatters']['json']['format'] = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "risk_management_service", "module": "%(module)s", "message": "%(message)s"}'

# Internal API Keys
INTERNAL_API_KEYS = [
    config('RISK_MANAGEMENT_API_KEY', default='dev-risk-management-key-123'),
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
    'TITLE': 'Risk Management Service API',
    'DESCRIPTION': 'API documentation for the Risk Management Service microservice. This service manages risk assessment, liability calculation, and monitoring for the betting system with 50+ sports and 50+ bet types.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_REQUEST': True,
    'SCHEMA_PATH_PREFIX': '/api/',
    'TAGS': [
        {'name': 'Risk Assessment', 'description': 'Risk assessment and monitoring endpoints'},
        {'name': 'Liability Calculation', 'description': 'Liability calculation and management'},
        {'name': 'Vigorish Management', 'description': 'Vigorish and margin management'},
        {'name': 'Pattern Analysis', 'description': 'Betting pattern analysis and detection'},
        {'name': 'Health Check', 'description': 'Service health and status endpoints'},
    ],
}
