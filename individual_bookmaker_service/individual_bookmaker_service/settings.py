"""
Django settings cho Individual Bookmaker Service.
"""

import sys
from pathlib import Path
from decouple import config

# Add parent directory to Python path to access shared module
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from shared.base_settings import *

SERVICE_NAME = 'individual_bookmaker_service'
SERVICE_PORT = 8007
SERVICE_VERSION = '1.0.0'

# Application definition
INSTALLED_APPS += [
    'individual_bookmaker',
]

ROOT_URLCONF = 'individual_bookmaker_service.urls'

# Database configuration for Individual Bookmaker Service
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='individual_bookmaker_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres123'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# Redis configuration for Individual Bookmaker Service
REDIS_DB = 7  # Use a different DB for each service
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# Internationalization
LANGUAGE_CODE = 'vi-vn'
TIME_ZONE = 'Asia/Ho_Chi_Minh'

# Logging for Individual Bookmaker Service
LOGGING['handlers']['file']['filename'] = BASE_DIR / 'logs' / 'individual_bookmaker.log'
LOGGING['loggers']['individual_bookmaker'] = {
    'handlers': ['console', 'file'],
    'level': 'DEBUG',
    'propagate': False,
}

# Add service name to log formatters
LOGGING['formatters']['json']['format'] = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "individual_bookmaker_service", "module": "%(module)s", "message": "%(message)s"}'

# External Service URLs
BETTING_SERVICE_URL = config('BETTING_SERVICE_URL', default='http://localhost:8002')
RISK_SERVICE_URL = config('RISK_SERVICE_URL', default='http://localhost:8003')
WALLET_SERVICE_URL = config('WALLET_SERVICE_URL', default='http://localhost:8004')

# Internal API Keys
INTERNAL_API_KEYS = [
    config('INDIVIDUAL_BOOKMAKER_API_KEY', default='dev-individual-bookmaker-key-123'),
    config('INTERNAL_API_KEY', default='dev-internal-key-456'),
]

# Rate Limiting Settings
RATE_LIMIT_MAX_REQUESTS = config('RATE_LIMIT_MAX_REQUESTS', default=100, cast=int)
RATE_LIMIT_WINDOW = config('RATE_LIMIT_WINDOW', default=60, cast=int)
