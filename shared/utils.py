"""
Common utilities shared across all microservices.
"""

import json
import logging
import requests
from typing import Dict, Any, Optional
from django.conf import settings
from django.core.cache import cache
from datetime import datetime, timedelta


logger = logging.getLogger(__name__)


class ServiceClient:
    """
    Base client for inter-service communication.
    """
    
    def __init__(self, service_name: str, base_url: str = None):
        self.service_name = service_name
        self.base_url = base_url or settings.MICROSERVICES.get(service_name)
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': f'SPORT_BETTING_MODULE/{service_name}'
        })
    
    def get(self, endpoint: str, params: Dict = None, timeout: int = 30) -> Dict[str, Any]:
        """Make GET request to service."""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.get(url, params=params, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling {self.service_name} GET {endpoint}: {e}")
            raise
    
    def post(self, endpoint: str, data: Dict = None, timeout: int = 30) -> Dict[str, Any]:
        """Make POST request to service."""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.post(url, json=data, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling {self.service_name} POST {endpoint}: {e}")
            raise
    
    def put(self, endpoint: str, data: Dict = None, timeout: int = 30) -> Dict[str, Any]:
        """Make PUT request to service."""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.put(url, json=data, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling {self.service_name} PUT {endpoint}: {e}")
            raise
    
    def delete(self, endpoint: str, timeout: int = 30) -> Dict[str, Any]:
        """Make DELETE request to service."""
        try:
            url = f"{self.base_url}{endpoint}"
            response = self.session.delete(url, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling {self.service_name} DELETE {endpoint}: {e}")
            raise


class CacheManager:
    """
    Centralized cache management.
    """
    
    @staticmethod
    def get(key: str, default=None):
        """Get value from cache."""
        try:
            return cache.get(key, default)
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return default
    
    @staticmethod
    def set(key: str, value: Any, timeout: int = 300):
        """Set value in cache."""
        try:
            cache.set(key, value, timeout)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
    
    @staticmethod
    def delete(key: str):
        """Delete value from cache."""
        try:
            cache.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
    
    @staticmethod
    def get_or_set(key: str, callable_func, timeout: int = 300):
        """Get value from cache or set it using callable."""
        try:
            return cache.get_or_set(key, callable_func, timeout)
        except Exception as e:
            logger.error(f"Cache get_or_set error for key {key}: {e}")
            return callable_func()


class HealthChecker:
    """
    Health check utilities for services.
    """
    
    @staticmethod
    def check_database():
        """Check database connectivity."""
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    @staticmethod
    def check_redis():
        """Check Redis connectivity."""
        try:
            cache.get('health_check')
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False
    
    @staticmethod
    def check_service(service_name: str, endpoint: str = '/health/'):
        """Check external service health."""
        try:
            client = ServiceClient(service_name)
            response = client.get(endpoint, timeout=5)
            return response.get('status') == 'healthy'
        except Exception as e:
            logger.error(f"Service {service_name} health check failed: {e}")
            return False


class ResponseFormatter:
    """
    Standardize API responses across services.
    """
    
    @staticmethod
    def success(data: Any = None, message: str = "Success", status_code: int = 200):
        """Format successful response."""
        return {
            'success': True,
            'message': message,
            'data': data,
            'status_code': status_code,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def error(message: str = "Error", errors: Dict = None, status_code: int = 400):
        """Format error response."""
        return {
            'success': False,
            'message': message,
            'errors': errors or {},
            'status_code': status_code,
            'timestamp': datetime.now().isoformat()
        }
    
    @staticmethod
    def paginated(data: list, page: int, page_size: int, total: int):
        """Format paginated response."""
        return {
            'success': True,
            'data': data,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': (total + page_size - 1) // page_size
            },
            'timestamp': datetime.now().isoformat()
        }


class DataValidator:
    """
    Common data validation utilities.
    """
    
    @staticmethod
    def validate_required_fields(data: Dict, required_fields: list) -> Dict[str, list]:
        """Validate required fields in data."""
        errors = {}
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == '':
                if 'required' not in errors:
                    errors['required'] = []
                errors['required'].append(field)
        return errors
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format."""
        import re
        pattern = r'^\+?1?\d{9,15}$'
        return re.match(pattern, phone) is not None


class SecurityUtils:
    """
    Security utilities for all services.
    """
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate secure API key."""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password securely."""
        from django.contrib.auth.hashers import make_password
        return make_password(password)
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash."""
        from django.contrib.auth.hashers import check_password
        return check_password(password, hashed)
