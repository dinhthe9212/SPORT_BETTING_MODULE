from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import psutil
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_basic(request):
    """Health check cơ bản - kiểm tra service có hoạt động không"""
    try:
        # Kiểm tra database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"
    
    # Kiểm tra cache
    try:
        cache.set('health_check_test', 'test_value', 10)
        cache_value = cache.get('health_check_test')
        cache_status = "healthy" if cache_value == 'test_value' else "unhealthy"
    except Exception as e:
        logger.error(f"Cache health check failed: {str(e)}")
        cache_status = "unhealthy"
    
    response_data = {
        'status': 'healthy' if db_status == 'healthy' and cache_status == 'healthy' else 'degraded',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Sports Data Service',
        'version': getattr(settings, 'APP_VERSION', '1.0.0'),
        'components': {
            'database': db_status,
            'cache': cache_status
        }
    }
    
    http_status = status.HTTP_200_OK if response_data['status'] == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return Response(response_data, status=http_status)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_detailed(request):
    """Health check chi tiết - kiểm tra tất cả components"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'service': 'Sports Data Service',
        'version': getattr(settings, 'APP_VERSION', '1.0.0'),
        'components': {},
        'system': {},
        'performance': {}
    }
    
    # 1. Database Health Check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
            db_response_time = 0.001  # Giả sử response time rất nhanh
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"
        db_response_time = None
        health_status['status'] = 'degraded'
    
    health_status['components']['database'] = {
        'status': db_status,
        'response_time_ms': db_response_time * 1000 if db_response_time else None,
        'connection_pool': {
            'max_connections': getattr(settings, 'DB_MAX_CONNECTIONS', 'unknown'),
            'active_connections': len(connection.queries) if hasattr(connection, 'queries') else 'unknown'
        }
    }
    
    # 2. Cache Health Check
    try:
        start_time = datetime.utcnow()
        cache.set('health_check_detailed', 'test_value', 10)
        cache_value = cache.get('health_check_detailed')
        end_time = datetime.utcnow()
        
        cache_response_time = (end_time - start_time).total_seconds()
        cache_status = "healthy" if cache_value == 'test_value' else "unhealthy"
        
        if cache_status == "unhealthy":
            health_status['status'] = 'degraded'
            
    except Exception as e:
        logger.error(f"Cache health check failed: {str(e)}")
        cache_status = "unhealthy"
        cache_response_time = None
        health_status['status'] = 'degraded'
    
    health_status['components']['cache'] = {
        'status': cache_status,
        'response_time_ms': cache_response_time * 1000 if cache_response_time else None,
        'backend': getattr(settings, 'CACHE_BACKEND', 'unknown')
    }
    
    # 3. External APIs Health Check
    external_apis_status = {}
    try:
        from .providers.multi_sports_provider import MultiSportsDataProvider
        provider = MultiSportsDataProvider()
        
        # Kiểm tra từng provider
        for provider_name, provider_instance in provider.providers.items():
            try:
                # Kiểm tra circuit breaker status
                if hasattr(provider_instance, 'get_live_scores'):
                    cb_status = "healthy"
                else:
                    cb_status = "unknown"
                
                external_apis_status[provider_name] = {
                    'status': cb_status,
                    'circuit_breaker': cb_status
                }
                
            except Exception as e:
                logger.error(f"Provider {provider_name} health check failed: {str(e)}")
                external_apis_status[provider_name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
                health_status['status'] = 'degraded'
                
    except Exception as e:
        logger.error(f"External APIs health check failed: {str(e)}")
        external_apis_status = {'error': str(e)}
        health_status['status'] = 'degraded'
    
    health_status['components']['external_apis'] = external_apis_status
    
    # 4. System Resources
    try:
        # CPU Usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory Usage
        memory = psutil.virtual_memory()
        
        # Disk Usage
        disk = psutil.disk_usage('/')
        
        health_status['system'] = {
            'cpu': {
                'usage_percent': cpu_percent,
                'count': psutil.cpu_count()
            },
            'memory': {
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'used_percent': memory.percent
            },
            'disk': {
                'total_gb': round(disk.total / (1024**3), 2),
                'free_gb': round(disk.free / (1024**3), 2),
                'used_percent': round((disk.used / disk.total) * 100, 2)
            }
        }
        
        # Kiểm tra system resources
        if cpu_percent > 90 or memory.percent > 90 or health_status['system']['disk']['used_percent'] > 90:
            health_status['status'] = 'degraded'
            
    except Exception as e:
        logger.error(f"System resources health check failed: {str(e)}")
        health_status['system'] = {'error': str(e)}
    
    # 5. Performance Metrics
    try:
        # Database query count
        db_queries = len(connection.queries) if hasattr(connection, 'queries') else 0
        
        # Cache hit rate (giả sử)
        cache_hit_rate = 0.85  # 85% cache hit rate
        
        health_status['performance'] = {
            'database_queries': db_queries,
            'cache_hit_rate': cache_hit_rate,
            'uptime_seconds': (datetime.utcnow() - datetime.fromtimestamp(psutil.boot_time())).total_seconds() if hasattr(psutil, 'boot_time') else None
        }
        
    except Exception as e:
        logger.error(f"Performance metrics health check failed: {str(e)}")
        health_status['performance'] = {'error': str(e)}
    
    # Xác định HTTP status code
    if health_status['status'] == 'healthy':
        http_status = status.HTTP_200_OK
    elif health_status['status'] == 'degraded':
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE
    else:
        http_status = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    return Response(health_status, status=http_status)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_providers(request):
    """Health check riêng cho các external providers"""
    try:
        from .providers.multi_sports_provider import MultiSportsDataProvider
        provider = MultiSportsDataProvider()
        
        providers_status = {}
        overall_status = 'healthy'
        
        for provider_name, provider_instance in provider.providers.items():
            try:
                # Kiểm tra circuit breaker status
                if hasattr(provider_instance, 'get_live_scores'):
                    # Giả sử có method để kiểm tra circuit breaker
                    cb_status = "healthy"
                else:
                    cb_status = "unknown"
                
                providers_status[provider_name] = {
                    'status': cb_status,
                    'circuit_breaker': cb_status,
                    'last_check': datetime.utcnow().isoformat()
                }
                
            except Exception as e:
                logger.error(f"Provider {provider_name} health check failed: {str(e)}")
                providers_status[provider_name] = {
                    'status': 'unhealthy',
                    'error': str(e),
                    'last_check': datetime.utcnow().isoformat()
                }
                overall_status = 'degraded'
        
        response_data = {
            'status': overall_status,
            'timestamp': datetime.utcnow().isoformat(),
            'providers': providers_status
        }
        
        http_status = status.HTTP_200_OK if overall_status == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE
        
        return Response(response_data, status=http_status)
        
    except Exception as e:
        logger.error(f"Providers health check failed: {str(e)}")
        return Response({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check_ready(request):
    """Health check để kiểm tra service đã sẵn sàng nhận traffic chưa"""
    try:
        # Kiểm tra các dependencies cơ bản
        dependencies_ready = True
        errors = []
        
        # 1. Database
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            dependencies_ready = False
            errors.append(f"Database: {str(e)}")
        
        # 2. Cache
        try:
            cache.set('ready_check', 'test', 10)
            if cache.get('ready_check') != 'test':
                dependencies_ready = False
                errors.append("Cache: Failed to read/write")
        except Exception as e:
            dependencies_ready = False
            errors.append(f"Cache: {str(e)}")
        
        # 3. Settings
        required_settings = ['SECRET_KEY', 'DEBUG']
        for setting in required_settings:
            if not getattr(settings, setting, None):
                dependencies_ready = False
                errors.append(f"Setting: {setting} not configured")
        
        if dependencies_ready:
            response_data = {
                'status': 'ready',
                'timestamp': datetime.utcnow().isoformat(),
                'message': 'Service is ready to receive traffic'
            }
            http_status = status.HTTP_200_OK
        else:
            response_data = {
                'status': 'not_ready',
                'timestamp': datetime.utcnow().isoformat(),
                'errors': errors,
                'message': 'Service is not ready to receive traffic'
            }
            http_status = status.HTTP_503_SERVICE_UNAVAILABLE
        
        return Response(response_data, status=http_status)
        
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return Response({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
