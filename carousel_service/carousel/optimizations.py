"""
Performance Optimizations for Carousel Service
Database query optimization, caching strategies
Cost: $0 (Django built-in optimizations)
"""

from django.db import models
from django.core.cache import cache
from django.db.models import Prefetch, Q, F, Count, Sum, Avg
from .models import FeaturedEvent, UserProductPurchase
from typing import List, Dict, Any
import logging

logger = logging.getLogger('carousel')


class OptimizedCarouselQueries:
    """Optimized database queries cho carousel"""
    
    @staticmethod
    def get_active_items_optimized(limit: int = 20) -> models.QuerySet:
        """
        Optimized query để lấy active carousel items
        Sử dụng select_related và prefetch_related để reduce N+1 queries
        """
        return FeaturedEvent.objects.select_related().filter(
            is_active=True
        ).prefetch_related(
            Prefetch(
                'user_purchases',
                queryset=UserProductPurchase.objects.filter(status='CONFIRMED'),
                to_attr='confirmed_purchases'
            )
        ).annotate(
            purchase_count=Count('user_purchases'),
            total_stake_amount=Sum('user_purchases__stake_amount'),
            avg_stake_amount=Avg('user_purchases__stake_amount')
        ).order_by('order', '-popularity_score')[:limit]
    
    @staticmethod
    def get_user_purchases_optimized(user_id: int, item_ids: List[int] = None) -> Dict[int, bool]:
        """
        Optimized query để check user purchases cho multiple items
        Single query thay vì N queries
        """
        cache_key = f"user_purchases:{user_id}"
        cached_purchases = cache.get(cache_key)
        
        if cached_purchases is not None:
            return cached_purchases
        
        # Build query
        query = UserProductPurchase.objects.filter(
            user_id=user_id,
            status__in=['PENDING', 'CONFIRMED']
        )
        
        if item_ids:
            query = query.filter(featured_event_id__in=item_ids)
        
        # Get all user purchases in single query
        purchases = query.values_list('featured_event_id', flat=True)
        purchase_dict = {item_id: item_id in purchases for item_id in (item_ids or [])}
        
        # Cache for 5 minutes
        cache.set(cache_key, purchase_dict, 300)
        
        return purchase_dict
    
    @staticmethod
    def get_trending_items_optimized(hours: int = 24, limit: int = 10) -> models.QuerySet:
        """
        Optimized query cho trending items
        Sử dụng database aggregation thay vì Python loops
        """
        from django.utils import timezone
        from datetime import timedelta
        
        since = timezone.now() - timedelta(hours=hours)
        
        return FeaturedEvent.objects.filter(
            is_active=True,
            user_purchases__purchased_at__gte=since
        ).annotate(
            recent_purchase_count=Count(
                'user_purchases',
                filter=Q(user_purchases__purchased_at__gte=since)
            ),
            recent_unique_users=Count(
                'user_purchases__user',
                distinct=True,
                filter=Q(user_purchases__purchased_at__gte=since)
            ),
            recent_total_stake=Sum(
                'user_purchases__stake_amount',
                filter=Q(user_purchases__purchased_at__gte=since)
            ),
            trend_score=F('recent_purchase_count') * 0.4 + 
                       F('recent_unique_users') * 0.3 +
                       F('popularity_score') * 0.3
        ).filter(
            recent_purchase_count__gt=0
        ).order_by('-trend_score')[:limit]


class PerformanceMiddleware:
    """
    Custom middleware cho performance optimizations
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Pre-processing
        self.process_request(request)
        
        response = self.get_response(request)
        
        # Post-processing
        self.process_response(request, response)
        
        return response
    
    def process_request(self, request):
        """Pre-processing optimizations"""
        # Add request timing
        import time
        request.start_time = time.time()
        
        # Enable query logging in debug mode
        if hasattr(request, 'user') and request.user.is_staff:
            from django.conf import settings
            if settings.DEBUG:
                from django.db import connection
                connection.queries_log.clear()
    
    def process_response(self, request, response):
        """Post-processing optimizations"""
        # Add response time header
        if hasattr(request, 'start_time'):
            import time
            response_time = time.time() - request.start_time
            response['X-Response-Time'] = f"{response_time:.3f}s"
        
        # Add query count header (debug only)
        if hasattr(request, 'user') and request.user.is_staff:
            from django.conf import settings
            if settings.DEBUG:
                from django.db import connection
                response['X-DB-Queries'] = len(connection.queries)
        
        # Add cache headers
        if request.method == 'GET' and response.status_code == 200:
            if 'carousel' in request.path:
                response['Cache-Control'] = 'public, max-age=300'  # 5 minutes
            elif 'analytics' in request.path:
                response['Cache-Control'] = 'public, max-age=900'  # 15 minutes
        
        return response


class CacheOptimizer:
    """
    Cache optimization strategies
    """
    
    @staticmethod
    def warm_cache_for_popular_items():
        """
        Warm cache cho popular carousel items
        Chạy as background task
        """
        try:
            # Get top 50 popular items
            popular_items = FeaturedEvent.objects.filter(
                is_active=True
            ).order_by('-popularity_score', '-total_purchases')[:50]
            
            # Pre-cache different device types
            device_types = ['mobile', 'tablet', 'desktop']
            
            for device_type in device_types:
                cache_key = f"popular_items:{device_type}"
                
                # Prepare data structure similar to API response
                items_data = []
                for item in popular_items:
                    items_data.append({
                        'id': item.id,
                        'title': item.title,
                        'current_odds': float(item.current_odds),
                        'total_purchases': item.total_purchases,
                        'popularity_score': item.popularity_score
                    })
                
                # Cache for 10 minutes
                cache.set(cache_key, items_data, 600)
            
            logger.info(f"Cache warmed for {len(popular_items)} popular items")
            
        except Exception as e:
            logger.error(f"Error warming cache: {e}")
    
    @staticmethod
    def get_or_set_cache(key: str, callable_func, timeout: int = 300):
        """
        Generic cache get-or-set helper
        """
        try:
            cached_value = cache.get(key)
            if cached_value is not None:
                return cached_value
            
            # Generate fresh value
            fresh_value = callable_func()
            cache.set(key, fresh_value, timeout)
            
            return fresh_value
            
        except Exception as e:
            logger.error(f"Cache error for key {key}: {e}")
            # Fallback to direct call
            return callable_func()


class DatabaseOptimizer:
    """
    Database optimization utilities
    """
    
    @staticmethod
    def get_database_stats() -> Dict[str, Any]:
        """
        Get database performance statistics
        """
        try:
            from django.db import connection
            
            # Get table sizes
            with connection.cursor() as cursor:
                # SQLite specific queries
                cursor.execute("""
                    SELECT name, 
                           COUNT(*) as row_count
                    FROM sqlite_master 
                    WHERE type='table' 
                    AND name LIKE 'carousel_%'
                """)
                
                table_stats = {}
                for table_name, row_count in cursor.fetchall():
                    table_stats[table_name] = {
                        'row_count': row_count
                    }
                
                # Get index information
                cursor.execute("""
                    SELECT name, sql 
                    FROM sqlite_master 
                    WHERE type='index' 
                    AND name LIKE 'carousel_%'
                """)
                
                indexes = []
                for index_name, sql in cursor.fetchall():
                    indexes.append({
                        'name': index_name,
                        'sql': sql
                    })
                
                return {
                    'tables': table_stats,
                    'indexes': indexes,
                    'total_queries_today': getattr(connection, 'queries_count', 0)
                }
                
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {'error': str(e)}
    
    @staticmethod
    def analyze_slow_queries() -> List[Dict[str, Any]]:
        """
        Analyze potentially slow queries
        """
        # This would integrate with query logging
        # For now, return sample data
        return [
            {
                'query': 'SELECT * FROM carousel_featuredevent WHERE is_active=1',
                'avg_time': 0.05,
                'call_count': 150,
                'optimization': 'Add index on is_active'
            }
        ]


# Performance monitoring decorator
def monitor_performance(func):
    """
    Decorator để monitor function performance
    """
    def wrapper(*args, **kwargs):
        import time
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            logger.info(f"Function {func.__name__} took {duration:.3f}s")
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Function {func.__name__} failed after {duration:.3f}s: {e}")
            raise
    
    return wrapper
