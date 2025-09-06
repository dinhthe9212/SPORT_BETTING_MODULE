"""
Common constants shared across all microservices.
"""

# Service Names
SERVICE_NAMES = {
    'AUTH': 'auth_service',
    'BETTING': 'betting_service',
    'RISK': 'risk_management_service',
    'WALLET': 'wallet_service',
    'SPORTS': 'sports_data_service',
    'CAROUSEL': 'carousel_service',
    'INDIVIDUAL_BOOKMAKER': 'individual_bookmaker_service',
    'SAGA': 'saga_orchestrator',
    'PROMOTIONS': 'promotions_service',
    'GROUPS': 'groups_service',
    'PAYMENT': 'payment_service',
}

# Service Ports
SERVICE_PORTS = {
    'AUTH': 8001,
    'BETTING': 8002,
    'RISK': 8003,
    'WALLET': 8004,
    'SPORTS': 8005,
    'CAROUSEL': 8006,
    'INDIVIDUAL_BOOKMAKER': 8007,
    'SAGA': 8008,
    'PROMOTIONS': 8009,
    'GROUPS': 8010,
    'PAYMENT': 8011,
}

# Common Status Codes
STATUS_CODES = {
    'ACTIVE': 'active',
    'INACTIVE': 'inactive',
    'PENDING': 'pending',
    'COMPLETED': 'completed',
    'FAILED': 'failed',
    'CANCELLED': 'cancelled',
    'SUSPENDED': 'suspended',
    'PROCESSING': 'processing',
}

# Betting Related Constants
BET_STATUS = {
    'PENDING': 'pending',
    'CONFIRMED': 'confirmed',
    'SETTLED': 'settled',
    'CANCELLED': 'cancelled',
    'CASHED_OUT': 'cashed_out',
}

BET_TYPE = {
    'SINGLE': 'single',
    'MULTIPLE': 'multiple',
    'SYSTEM': 'system',
    'LIVE': 'live',
}

SPORT_CATEGORIES = {
    'BALL_SPORTS': 'ball_sports',
    'RACING': 'racing',
    'COMBAT': 'combat',
    'INDIVIDUAL': 'individual',
    'WINTER': 'winter',
    'WATER': 'water',
    'MOTOR': 'motor',
    'SPECIAL': 'special',
}

BET_TYPE_CATEGORIES = {
    'MATCH_RESULT': 'match_result',
    'SCORING': 'scoring',
    'PERFORMANCE': 'performance',
    'SPECIAL_EVENTS': 'special_events',
    'COMBINATIONS': 'combinations',
    'FUTURES': 'futures',
    'LIVE_BETTING': 'live_betting',
    'SPECIAL_MARKETS': 'special_markets',
}

# Risk Management Constants
RISK_LEVELS = {
    'LOW': 'low',
    'MEDIUM': 'medium',
    'HIGH': 'high',
    'CRITICAL': 'critical',
}

BOOKMAKER_TYPES = {
    'SYSTEM': 'system',
    'INDIVIDUAL': 'individual',
    'GROUP': 'group',
}

# Saga Constants
SAGA_STATUS = {
    'STARTED': 'started',
    'IN_PROGRESS': 'in_progress',
    'COMPLETED': 'completed',
    'FAILED': 'failed',
    'COMPENSATED': 'compensated',
}

SAGA_STEP_STATUS = {
    'PENDING': 'pending',
    'IN_PROGRESS': 'in_progress',
    'COMPLETED': 'completed',
    'FAILED': 'failed',
    'COMPENSATED': 'compensated',
}

# Cache Keys
CACHE_KEYS = {
    'USER_SESSION': 'user_session:{user_id}',
    'BETTING_ODDS': 'betting_odds:{match_id}',
    'RISK_THRESHOLD': 'risk_threshold:{bookmaker_id}',
    'SPORTS_DATA': 'sports_data:{sport_id}',
    'CAROUSEL_ITEMS': 'carousel_items:{category}',
    'SAGA_STATUS': 'saga_status:{saga_id}',
}

# Cache Timeouts (in seconds)
CACHE_TIMEOUTS = {
    'SHORT': 300,      # 5 minutes
    'MEDIUM': 1800,    # 30 minutes
    'LONG': 3600,      # 1 hour
    'VERY_LONG': 86400, # 24 hours
}

# API Response Messages
API_MESSAGES = {
    'SUCCESS': 'Operation completed successfully',
    'ERROR': 'An error occurred',
    'NOT_FOUND': 'Resource not found',
    'UNAUTHORIZED': 'Unauthorized access',
    'FORBIDDEN': 'Access forbidden',
    'VALIDATION_ERROR': 'Validation error',
    'RATE_LIMIT_EXCEEDED': 'Rate limit exceeded',
    'SERVICE_UNAVAILABLE': 'Service temporarily unavailable',
}

# Error Codes
ERROR_CODES = {
    'VALIDATION_ERROR': 'VALIDATION_ERROR',
    'AUTHENTICATION_ERROR': 'AUTHENTICATION_ERROR',
    'AUTHORIZATION_ERROR': 'AUTHORIZATION_ERROR',
    'NOT_FOUND_ERROR': 'NOT_FOUND_ERROR',
    'RATE_LIMIT_ERROR': 'RATE_LIMIT_ERROR',
    'SERVICE_ERROR': 'SERVICE_ERROR',
    'DATABASE_ERROR': 'DATABASE_ERROR',
    'EXTERNAL_API_ERROR': 'EXTERNAL_API_ERROR',
}

# Pagination
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Rate Limiting
DEFAULT_RATE_LIMIT = {
    'REQUESTS_PER_MINUTE': 100,
    'REQUESTS_PER_HOUR': 1000,
    'REQUESTS_PER_DAY': 10000,
}

# File Upload
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_FILE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'application/pdf']

# Timeouts
DEFAULT_TIMEOUT = 30  # seconds
LONG_TIMEOUT = 120    # seconds
SHORT_TIMEOUT = 5     # seconds
