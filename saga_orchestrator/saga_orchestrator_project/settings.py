import sys
from pathlib import Path
from decouple import config

# Add parent directory to Python path to access shared module
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from shared.base_settings import *

SERVICE_NAME = 'saga_orchestrator'
SERVICE_PORT = 8008
SERVICE_VERSION = '1.0.0'

# Application definition
INSTALLED_APPS += [
    'sagas',
]

ROOT_URLCONF = 'saga_orchestrator_project.urls'

# Database configuration for Saga Orchestrator
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='saga_db'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres123'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# Redis configuration for Saga Orchestrator
REDIS_DB = 8  # Use a different DB for each service
CELERY_BROKER_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
CELERY_RESULT_BACKEND = f'redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = config('KAFKA_BOOTSTRAP_SERVERS', default='kafka:9092')
KAFKA_CONSUMER_GROUP = 'saga_orchestrator'

# Saga configuration
SAGA_TIMEOUT = config('SAGA_TIMEOUT', default=300, cast=int)  # 5 minutes
SAGA_RETRY_ATTEMPTS = config('SAGA_RETRY_ATTEMPTS', default=3, cast=int)
SAGA_RETRY_DELAY = config('SAGA_RETRY_DELAY', default=5, cast=int)  # seconds

# Internal API Keys
INTERNAL_API_KEYS = [
    config('SAGA_API_KEY', default='dev-saga-key-123'),
    config('INTERNAL_API_KEY', default='dev-internal-key-456'),
]

# Rate Limiting Settings
RATE_LIMIT_MAX_REQUESTS = config('RATE_LIMIT_MAX_REQUESTS', default=100, cast=int)
RATE_LIMIT_WINDOW = config('RATE_LIMIT_WINDOW', default=60, cast=int)

# Logging for Saga Orchestrator
LOGGING['handlers']['file']['filename'] = BASE_DIR / 'logs' / 'saga_orchestrator.log'
LOGGING['loggers']['sagas'] = {
    'handlers': ['console', 'file'],
    'level': 'DEBUG',
    'propagate': False,
}

# Add service name to log formatters
LOGGING['formatters']['json']['format'] = '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "service": "saga_orchestrator", "module": "%(module)s", "message": "%(message)s"}'

