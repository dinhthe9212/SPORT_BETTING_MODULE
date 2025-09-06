"""
Analytics Views for Carousel Service
Rule-based analytics endpoints - NO AI/ML
Cost: $0 (Pure statistical analysis)
"""

from django.http import JsonResponse
from django.views import View
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .analytics_service import CarouselAnalyticsService
import logging

logger = logging.getLogger('carousel')


class TrendingItemsView(View):
    """View để lấy trending items"""
    
    def get(self, request):
        """Get trending items với rule-based analysis"""
        try:
            hours = int(request.GET.get('hours', 24))
            limit = int(request.GET.get('limit', 10))
            
            # Validate parameters
            if hours > 168:  # Max 1 week
                hours = 168
            if limit > 50:   # Max 50 items
                limit = 50
            
            trending_items = CarouselAnalyticsService.get_trending_items(
                hours=hours,
                limit=limit
            )
            
            return JsonResponse({
                'status': 'success',
                'period_hours': hours,
                'trending_items': trending_items,
                'total_items': len(trending_items),
                'timestamp': timezone.now().isoformat()
            })
            
        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid parameters'
            }, status=400)
        except Exception as e:
            logger.error(f"Error getting trending items: {e}")
            return JsonResponse({
                'status': 'error',
                'message': 'Internal server error'
            }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_behavior_analytics(request):
    """
    API endpoint cho user behavior analytics
    User có thể xem analytics của chính mình
    Admin có thể xem analytics của user khác
    """
    try:
        # Get parameters
        target_user_id = request.query_params.get('user_id')
        days = int(request.query_params.get('days', 30))
        
        # Validate days parameter
        if days > 365:  # Max 1 year
            days = 365
        
        # Permission check
        if target_user_id:
            if not request.user.is_staff and int(target_user_id) != request.user.id:
                return Response({
                    'error': 'Permission denied - can only view own analytics'
                }, status=403)
            user_id = int(target_user_id)
        else:
            user_id = request.user.id
        
        analytics = CarouselAnalyticsService.get_user_behavior_patterns(
            user_id=user_id,
            days=days
        )
        
        return Response({
            'status': 'success',
            'user_id': user_id,
            'analytics': analytics,
            'timestamp': timezone.now().isoformat()
        })
        
    except ValueError as e:
        return Response({
            'status': 'error',
            'message': 'Invalid parameters'
        }, status=400)
    except Exception as e:
        logger.error(f"Error getting user behavior analytics: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def conversion_analytics(request):
    """
    API endpoint cho conversion analytics
    Chỉ admin mới có thể access
    """
    try:
        days = int(request.query_params.get('days', 7))
        
        # Validate days parameter
        if days > 90:  # Max 90 days
            days = 90
        
        analytics = CarouselAnalyticsService.get_conversion_analytics(days=days)
        
        return Response({
            'status': 'success',
            'analytics': analytics,
            'timestamp': timezone.now().isoformat()
        })
        
    except ValueError as e:
        return Response({
            'status': 'error',
            'message': 'Invalid parameters'
        }, status=400)
    except Exception as e:
        logger.error(f"Error getting conversion analytics: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error'
        }, status=500)


@api_view(['GET'])
def public_analytics_summary(request):
    """
    Public analytics summary - không cần authentication
    Chỉ hiển thị basic stats, không sensitive data
    """
    try:
        hours = int(request.query_params.get('hours', 24))
        if hours > 168:  # Max 1 week
            hours = 168
        
        # Get basic trending data (sanitized)
        trending_items = CarouselAnalyticsService.get_trending_items(
            hours=hours,
            limit=5  # Only top 5 for public
        )
        
        # Remove sensitive data
        public_trending = []
        for item in trending_items:
            public_trending.append({
                'item_id': item['item_id'],
                'title': item['title'],
                'trend_score': item['trend_score'],
                'popularity_rank': len(public_trending) + 1
            })
        
        return Response({
            'status': 'success',
            'period_hours': hours,
            'top_trending': public_trending,
            'total_trending_items': len(public_trending),
            'timestamp': timezone.now().isoformat(),
            'note': 'Public summary - limited data'
        })
        
    except ValueError as e:
        return Response({
            'status': 'error',
            'message': 'Invalid parameters'
        }, status=400)
    except Exception as e:
        logger.error(f"Error getting public analytics: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error'
        }, status=500)


class AnalyticsDashboardView(View):
    """
    Simple analytics dashboard view
    Tổng hợp multiple analytics cho admin interface
    """
    
    def get(self, request):
        """Get comprehensive analytics dashboard"""
        try:
            # Check admin permission
            if not request.user.is_authenticated or not request.user.is_staff:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Admin access required'
                }, status=403)
            
            # Get various analytics
            dashboard_data = {
                'trending_items': CarouselAnalyticsService.get_trending_items(
                    hours=24, limit=10
                ),
                'conversion_stats': CarouselAnalyticsService.get_conversion_analytics(
                    days=7
                ),
                'timestamp': timezone.now().isoformat(),
                'dashboard_info': {
                    'last_updated': timezone.now().isoformat(),
                    'data_sources': ['carousel_purchases', 'featured_events'],
                    'analysis_type': 'rule_based_statistical',
                    'ai_ml_used': False
                }
            }
            
            return JsonResponse({
                'status': 'success',
                'dashboard': dashboard_data
            })
            
        except Exception as e:
            logger.error(f"Error generating analytics dashboard: {e}")
            return JsonResponse({
                'status': 'error',
                'message': 'Internal server error'
            }, status=500)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def refresh_analytics_cache(request):
    """
    Endpoint để refresh analytics cache
    Chỉ admin có thể trigger
    """
    try:
        # Trong real implementation, đây sẽ clear cache
        # và trigger re-calculation của analytics
        
        # For now, just return success
        return Response({
            'status': 'success',
            'message': 'Analytics cache refresh triggered',
            'timestamp': timezone.now().isoformat(),
            'note': 'Cache refresh implementation pending'
        })
        
    except Exception as e:
        logger.error(f"Error refreshing analytics cache: {e}")
        return Response({
            'status': 'error',
            'message': 'Internal server error'
        }, status=500)
