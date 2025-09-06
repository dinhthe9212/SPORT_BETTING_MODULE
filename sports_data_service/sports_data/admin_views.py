"""
Admin Views cho Sports Data Service
Cung cấp API endpoints cho Admin Panel để quản lý và truy cập dữ liệu tham khảo
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.utils import timezone
from django.core.cache import cache
import logging

from .providers.multi_sports_provider import MultiSportsDataProvider
from .alerting.alert_manager import alert_manager
from .conflict_resolution.conflict_manager import conflict_resolution_manager
from .models import Sport, Match, Team, SportsDataProvider as ProviderModel

logger = logging.getLogger(__name__)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_dashboard_data(request):
    """
    Lấy dữ liệu tổng quan cho Admin Dashboard
    """
    try:
        # Khởi tạo sports service
        sports_service = MultiSportsDataProvider()
        
        # Lấy thống kê cơ bản
        total_sports = Sport.objects.filter(is_active=True).count()
        total_matches = Match.objects.count()
        live_matches = Match.objects.filter(status='LIVE').count()
        total_teams = Team.objects.count()
        
        # Lấy Circuit Breaker status
        circuit_breaker_status = sports_service.get_circuit_breaker_status()
        system_health = sports_service.get_system_health_summary()
        
        # Lấy Alert statistics
        alert_stats = alert_manager.get_alert_statistics(hours=24)
        
        # Lấy Conflict statistics
        conflict_stats = conflict_resolution_manager.get_conflict_statistics()
        
        dashboard_data = {
            'timestamp': timezone.now().isoformat(),
            'sports_data': {
                'total_sports': total_sports,
                'total_matches': total_matches,
                'live_matches': live_matches,
                'total_teams': total_teams
            },
            'system_health': system_health,
            'circuit_breakers': circuit_breaker_status,
            'alerts': alert_stats,
            'conflicts': conflict_stats,
            'cache_status': {
                'redis_connected': cache.get('health_check', None) is not None
            }
        }
        
        return Response({
            'status': 'success',
            'data': dashboard_data
        })
        
    except Exception as e:
        logger.error(f"Error getting admin dashboard data: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_reference_odds(request):
    """
    Lấy tỷ lệ cược tham khảo từ The-Odds-API cho Admin
    """
    try:
        sport = request.GET.get('sport', 'football')
        match_id = request.GET.get('match_id')
        
        # Khởi tạo sports service
        sports_service = MultiSportsDataProvider()
        
        # Lấy reference odds từ The-Odds-API
        odds_provider = sports_service.providers.get('odds_api')
        if odds_provider and hasattr(odds_provider, 'get_reference_odds'):
            reference_odds = odds_provider.get_reference_odds(sport, match_id)
        else:
            reference_odds = {}
        
        return Response({
            'status': 'success',
            'data': reference_odds,
            'metadata': {
                'sport': sport,
                'match_id': match_id,
                'source': 'the_odds_api',
                'timestamp': timezone.now().isoformat(),
                'note': 'Reference data only - not for user display'
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting reference odds: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_market_analysis(request):
    """
    Lấy phân tích thị trường cược cho Admin
    """
    try:
        sport = request.GET.get('sport', 'football')
        
        # Khởi tạo sports service
        sports_service = MultiSportsDataProvider()
        
        # Lấy market analysis từ The-Odds-API
        odds_provider = sports_service.providers.get('odds_api')
        if odds_provider and hasattr(odds_provider, 'get_market_analysis'):
            market_analysis = odds_provider.get_market_analysis(sport)
        else:
            market_analysis = {}
        
        return Response({
            'status': 'success',
            'data': market_analysis,
            'metadata': {
                'sport': sport,
                'timestamp': timezone.now().isoformat(),
                'note': 'Market analysis for admin reference only'
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting market analysis: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_provider_markets(request):
    """
    Lấy danh sách markets từ API-Sports.io cho Admin
    """
    try:
        sport = request.GET.get('sport', 'football')
        
        # Khởi tạo sports service
        sports_service = MultiSportsDataProvider()
        
        # Lấy markets từ API-Sports.io
        api_sports_provider = sports_service.providers.get('api_sports')
        if api_sports_provider and hasattr(api_sports_provider, 'get_markets'):
            markets = api_sports_provider.get_markets(sport)
        else:
            markets = []
        
        return Response({
            'status': 'success',
            'data': {
                'sport': sport,
                'markets': markets,
                'total_markets': len(markets)
            },
            'metadata': {
                'source': 'api_sports_io',
                'timestamp': timezone.now().isoformat(),
                'note': 'Available betting markets for admin reference'
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting provider markets: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_circuit_breaker_status(request):
    """
    Lấy trạng thái Circuit Breaker của tất cả providers
    """
    try:
        # Khởi tạo sports service
        sports_service = MultiSportsDataProvider()
        
        # Lấy Circuit Breaker status
        circuit_breaker_status = sports_service.get_circuit_breaker_status()
        system_health = sports_service.get_system_health_summary()
        
        return Response({
            'status': 'success',
            'data': {
                'circuit_breakers': circuit_breaker_status,
                'system_health': system_health
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting circuit breaker status: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def reset_circuit_breaker(request):
    """
    Reset Circuit Breaker cho provider cụ thể
    """
    try:
        provider_name = request.data.get('provider_name')
        
        if not provider_name:
            return Response({
                'status': 'error',
                'message': 'provider_name is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Khởi tạo sports service
        sports_service = MultiSportsDataProvider()
        
        # Reset Circuit Breaker
        sports_service.force_reset_all_circuit_breakers()
        
        return Response({
            'status': 'success',
            'message': f'Circuit Breaker for {provider_name} has been reset'
        })
        
    except Exception as e:
        logger.error(f"Error resetting circuit breaker: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_active_conflicts(request):
    """
    Lấy danh sách xung đột dữ liệu đang hoạt động
    """
    try:
        active_conflicts = conflict_resolution_manager.get_active_conflicts()
        
        return Response({
            'status': 'success',
            'data': {
                'active_conflicts': active_conflicts,
                'total_active': len(active_conflicts)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting active conflicts: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def resolve_conflict_manually(request):
    """
    Giải quyết xung đột dữ liệu thủ công
    """
    try:
        conflict_id = request.data.get('conflict_id')
        resolution = request.data.get('resolution', {})
        resolved_by = request.user.username
        
        if not conflict_id:
            return Response({
                'status': 'error',
                'message': 'conflict_id is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Giải quyết xung đột
        success = conflict_resolution_manager.manual_resolve_conflict(
            conflict_id, resolution, resolved_by
        )
        
        if success:
            return Response({
                'status': 'success',
                'message': f'Conflict {conflict_id} has been resolved manually'
            })
        else:
            return Response({
                'status': 'error',
                'message': f'Could not resolve conflict {conflict_id}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Error manually resolving conflict: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_alert_history(request):
    """
    Lấy lịch sử cảnh báo
    """
    try:
        hours = int(request.GET.get('hours', 24))
        alert_history = alert_manager.get_alert_history(hours)
        alert_stats = alert_manager.get_alert_statistics(hours)
        
        return Response({
            'status': 'success',
            'data': {
                'alert_history': alert_history,
                'statistics': alert_stats
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting alert history: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def force_sync_data(request):
    """
    Buộc đồng bộ dữ liệu ngay lập tức
    """
    try:
        sync_type = request.data.get('sync_type', 'all')  # all, sports, odds
        sport = request.data.get('sport')
        
        # Khởi tạo sports service
        sports_service = MultiSportsDataProvider()
        
        if sync_type == 'sports':
            # Đồng bộ dữ liệu thể thao
            from django.core.management import call_command
            call_command('sync_sports_data', force=True, sport=sport)
            message = f'Sports data sync forced for {sport or "all sports"}'
            
        elif sync_type == 'odds':
            # Đồng bộ dữ liệu tỷ lệ cược
            from django.core.management import call_command
            call_command('sync_odds_data', force=True, sport=sport)
            message = f'Odds data sync forced for {sport or "all sports"}'
            
        else:
            # Đồng bộ tất cả
            from django.core.management import call_command
            call_command('sync_sports_data', force=True, sport=sport)
            call_command('sync_odds_data', force=True, sport=sport)
            message = f'All data sync forced for {sport or "all sports"}'
        
        return Response({
            'status': 'success',
            'message': message
        })
        
    except Exception as e:
        logger.error(f"Error forcing data sync: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_provider_performance(request):
    """
    Lấy hiệu suất của các providers
    """
    try:
        providers = ProviderModel.objects.all()
        provider_performance = []
        
        for provider in providers:
            performance = {
                'name': provider.name,
                'type': provider.provider_type,
                'data_accuracy': provider.data_accuracy,
                'update_speed': provider.update_speed,
                'coverage_rate': provider.coverage_rate,
                'performance_score': provider.get_performance_score(),
                'last_successful_update': provider.last_successful_update,
                'error_count': provider.error_count,
                'consecutive_failures': provider.consecutive_failures,
                'is_active': provider.is_active
            }
            provider_performance.append(performance)
        
        return Response({
            'status': 'success',
            'data': {
                'providers': provider_performance,
                'total_providers': len(provider_performance)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting provider performance: {str(e)}")
        return Response({
            'status': 'error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
