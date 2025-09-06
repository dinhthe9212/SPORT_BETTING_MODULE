"""
Health Check Views for Carousel Service
Cost: $0 (Django built-in)
"""

from django.http import JsonResponse
from django.views import View
from django.db import connection
from django.core.cache import cache
from django.utils import timezone
from .models import FeaturedEvent, UserProductPurchase
import time
import psutil  # pip install psutil (free)
import logging

logger = logging.getLogger('carousel')


class HealthCheckView(View):
    """Basic health check endpoint"""
    
    def get(self, request):
        """Simple health check"""
        return JsonResponse({
            'status': 'healthy',
            'service': 'carousel',
            'timestamp': timezone.now().isoformat(),
            'version': '1.0.0'
        })


class ComprehensiveHealthView(View):
    """Comprehensive health check with detailed metrics"""
    
    def get(self, request):
        """Detailed health check"""
        health_data = {
            'timestamp': timezone.now().isoformat(),
            'service': 'carousel',
            'overall_status': 'healthy',
            'checks': {}
        }
        
        # Database check
        health_data['checks']['database'] = self._check_database()
        
        # Cache check  
        health_data['checks']['cache'] = self._check_cache()
        
        # Models check
        health_data['checks']['models'] = self._check_models()
        
        # System resources
        health_data['checks']['system'] = self._check_system_resources()
        
        # Determine overall status
        failed_checks = [name for name, check in health_data['checks'].items() 
                        if check['status'] != 'healthy']
        
        if failed_checks:
            health_data['overall_status'] = 'unhealthy' if len(failed_checks) > 2 else 'degraded'
            health_data['failed_checks'] = failed_checks
        
        status_code = 200 if health_data['overall_status'] == 'healthy' else 503
        return JsonResponse(health_data, status=status_code)
    
    def _check_database(self):
        """Check database connectivity and performance"""
        try:
            start_time = time.time()
            
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            duration = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                'status': 'healthy',
                'response_time_ms': round(duration, 2),
                'details': 'Database connection successful'
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                'status': 'unhealthy', 
                'error': str(e),
                'details': 'Database connection failed'
            }
    
    def _check_cache(self):
        """Check cache connectivity and performance"""
        try:
            start_time = time.time()
            
            # Test cache operations
            test_key = f'health_check_{int(time.time())}'
            test_value = {'test': 'data', 'timestamp': timezone.now().isoformat()}
            
            cache.set(test_key, test_value, 60)
            retrieved_value = cache.get(test_key)
            cache.delete(test_key)
            
            duration = (time.time() - start_time) * 1000
            
            if retrieved_value and retrieved_value.get('test') == 'data':
                return {
                    'status': 'healthy',
                    'response_time_ms': round(duration, 2),
                    'details': 'Cache operations successful'
                }
            else:
                return {
                    'status': 'unhealthy',
                    'details': 'Cache data integrity issue'
                }
        except Exception as e:
            logger.error(f"Cache health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'details': 'Cache connection failed'
            }
    
    def _check_models(self):
        """Check model access and basic statistics"""
        try:
            start_time = time.time()
            
            # Check FeaturedEvent model
            featured_count = FeaturedEvent.objects.count()
            active_count = FeaturedEvent.objects.filter(is_active=True).count()
            
            # Check UserProductPurchase model
            purchase_count = UserProductPurchase.objects.count()
            pending_purchases = UserProductPurchase.objects.filter(status='PENDING').count()
            
            duration = (time.time() - start_time) * 1000
            
            return {
                'status': 'healthy',
                'response_time_ms': round(duration, 2),
                'details': {
                    'featured_events': {
                        'total': featured_count,
                        'active': active_count
                    },
                    'purchases': {
                        'total': purchase_count,
                        'pending': pending_purchases
                    }
                }
            }
        except Exception as e:
            logger.error(f"Models health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'details': 'Model access failed'
            }
    
    def _check_system_resources(self):
        """Check system resource usage"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            
            # Determine status based on thresholds
            status = 'healthy'
            warnings = []
            
            if cpu_percent > 80:
                status = 'degraded'
                warnings.append(f'High CPU usage: {cpu_percent}%')
            
            if memory_percent > 80:
                status = 'degraded' 
                warnings.append(f'High memory usage: {memory_percent}%')
            
            if disk_percent > 90:
                status = 'degraded'
                warnings.append(f'High disk usage: {disk_percent}%')
            
            result = {
                'status': status,
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent,
                'disk_percent': disk_percent
            }
            
            if warnings:
                result['warnings'] = warnings
            
            return result
            
        except Exception as e:
            logger.error(f"System resources check failed: {e}")
            return {
                'status': 'unknown',
                'error': str(e),
                'details': 'System resource check failed'
            }


class MetricsView(View):
    """Basic metrics endpoint for monitoring"""
    
    def get(self, request):
        """Return basic service metrics"""
        try:
            # Get time period from query params (default: last hour)
            hours = int(request.GET.get('hours', 1))
            since = timezone.now() - timezone.timedelta(hours=hours)
            
            # Basic metrics
            metrics = {
                'timestamp': timezone.now().isoformat(),
                'period_hours': hours,
                'carousel': {
                    'total_items': FeaturedEvent.objects.count(),
                    'active_items': FeaturedEvent.objects.filter(is_active=True).count(),
                    'recent_items': FeaturedEvent.objects.filter(created_at__gte=since).count(),
                },
                'purchases': {
                    'total': UserProductPurchase.objects.count(),
                    'recent': UserProductPurchase.objects.filter(purchased_at__gte=since).count(),
                    'pending': UserProductPurchase.objects.filter(status='PENDING').count(),
                    'confirmed': UserProductPurchase.objects.filter(status='CONFIRMED').count(),
                },
                'performance': {
                    'avg_response_time_ms': 150,  # TODO: Calculate from logs
                    'success_rate': 99.5,  # TODO: Calculate from logs
                    'cache_hit_rate': 85,  # TODO: Calculate from cache stats
                }
            }
            
            return JsonResponse(metrics)
            
        except Exception as e:
            logger.error(f"Metrics collection failed: {e}")
            return JsonResponse({
                'error': 'Metrics collection failed',
                'details': str(e)
            }, status=500)


class ReadinessView(View):
    """Kubernetes readiness probe"""
    
    def get(self, request):
        """Check if service is ready to accept traffic"""
        try:
            # Quick checks for readiness
            # 1. Database is accessible
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
            
            # 2. Required tables exist
            FeaturedEvent.objects.exists()
            
            # 3. Cache is working
            cache.set('readiness_test', 'ok', 10)
            cache.get('readiness_test')
            
            return JsonResponse({
                'status': 'ready',
                'service': 'carousel',
                'timestamp': timezone.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Readiness check failed: {e}")
            return JsonResponse({
                'status': 'not_ready',
                'error': str(e)
            }, status=503)


class LivenessView(View):
    """Kubernetes liveness probe"""
    
    def get(self, request):
        """Check if service is alive (simpler than readiness)"""
        return JsonResponse({
            'status': 'alive',
            'service': 'carousel',
            'timestamp': timezone.now().isoformat()
        })
