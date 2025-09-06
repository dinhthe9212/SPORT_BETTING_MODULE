"""
Common middleware for all microservices.
"""

import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Log all requests for monitoring and debugging.
    """
    
    def process_request(self, request):
        request.start_time = time.time()
        logger.info(f"Request started: {request.method} {request.path}")
    
    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            logger.info(f"Request completed: {request.method} {request.path} - {response.status_code} - {duration:.3f}s")
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware to prevent abuse.
    """
    
    def process_request(self, request):
        # Skip rate limiting for admin and health check endpoints
        if request.path.startswith('/admin/') or request.path.startswith('/health/'):
            return None
        
        # Get client IP
        client_ip = self.get_client_ip(request)
        
        # Create rate limit key
        rate_limit_key = f"rate_limit:{client_ip}"
        
        # Check current request count
        current_requests = cache.get(rate_limit_key, 0)
        
        # Set rate limit (100 requests per minute)
        max_requests = getattr(settings, 'RATE_LIMIT_MAX_REQUESTS', 100)
        rate_limit_window = getattr(settings, 'RATE_LIMIT_WINDOW', 60)
        
        if current_requests >= max_requests:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JsonResponse({
                'error': 'Rate limit exceeded',
                'message': f'Maximum {max_requests} requests per {rate_limit_window} seconds allowed'
            }, status=429)
        
        # Increment request count
        cache.set(rate_limit_key, current_requests + 1, rate_limit_window)
        
        return None
    
    def get_client_ip(self, request):
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Add security headers to all responses.
    """
    
    def process_response(self, request, response):
        # Add security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Add HSTS header for HTTPS
        if request.is_secure():
            response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response


class APIKeyAuthMiddleware(MiddlewareMixin):
    """
    API key authentication middleware for service-to-service communication.
    """
    
    def process_request(self, request):
        # Skip authentication for certain endpoints
        skip_paths = ['/admin/', '/health/', '/static/', '/media/']
        if any(request.path.startswith(path) for path in skip_paths):
            return None
        
        # Check for API key in headers
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None  # Let other authentication handle it
        
        # Validate API key
        valid_api_keys = getattr(settings, 'INTERNAL_API_KEYS', [])
        if api_key not in valid_api_keys:
            logger.warning(f"Invalid API key used: {api_key}")
            return JsonResponse({
                'error': 'Invalid API key',
                'message': 'The provided API key is not valid'
            }, status=401)
        
        return None


class ErrorHandlingMiddleware(MiddlewareMixin):
    """
    Global error handling middleware.
    """
    
    def process_exception(self, request, exception):
        logger.error(f"Unhandled exception: {exception}", exc_info=True)
        
        # Return JSON error response for API requests
        if request.path.startswith('/api/'):
            return JsonResponse({
                'error': 'Internal server error',
                'message': 'An unexpected error occurred',
                'status_code': 500
            }, status=500)
        
        # Let Django handle other exceptions
        return None


class ServiceIdentificationMiddleware(MiddlewareMixin):
    """
    Add service identification headers to responses.
    """
    
    def process_response(self, request, response):
        service_name = getattr(settings, 'SERVICE_NAME', 'unknown')
        service_version = getattr(settings, 'SERVICE_VERSION', '1.0.0')
        
        response['X-Service-Name'] = service_name
        response['X-Service-Version'] = service_version
        
        return response
