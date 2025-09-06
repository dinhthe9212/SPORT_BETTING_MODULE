from django.urls import path
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class APIVersionManager:
    """Quản lý phiên bản API"""
    
    def __init__(self):
        self.supported_versions = ['v1', 'v2']
        self.default_version = 'v1'
        self.version_deprecation = {
            'v1': {
                'deprecated': False,
                'deprecation_date': None,
                'sunset_date': None,
                'migration_guide': None
            },
            'v2': {
                'deprecated': False,
                'deprecation_date': None,
                'sunset_date': None,
                'migration_guide': None
            }
        }
        self.version_features = {
            'v1': {
                'basic_sports_data': True,
                'live_scores': True,
                'fixtures': True,
                'odds_data': True,
                'team_info': True,
                'league_info': True
            },
            'v2': {
                'basic_sports_data': True,
                'live_scores': True,
                'fixtures': True,
                'odds_data': True,
                'team_info': True,
                'league_info': True,
                'advanced_analytics': True,
                'real_time_updates': True,
                'bulk_operations': True,
                'filtering_and_sorting': True
            }
        }
    
    def get_supported_versions(self) -> List[str]:
        """Lấy danh sách phiên bản được hỗ trợ"""
        return self.supported_versions
    
    def is_version_supported(self, version: str) -> bool:
        """Kiểm tra phiên bản có được hỗ trợ không"""
        return version in self.supported_versions
    
    def get_default_version(self) -> str:
        """Lấy phiên bản mặc định"""
        return self.default_version
    
    def get_version_info(self, version: str) -> Dict[str, Any]:
        """Lấy thông tin chi tiết về phiên bản"""
        if not self.is_version_supported(version):
            return {
                'error': f'Version {version} is not supported',
                'supported_versions': self.supported_versions
            }
        
        return {
            'version': version,
            'deprecated': self.version_deprecation[version]['deprecated'],
            'deprecation_date': self.version_deprecation[version]['deprecation_date'],
            'sunset_date': self.version_deprecation[version]['sunset_date'],
            'migration_guide': self.version_deprecation[version]['migration_guide'],
            'features': self.version_features[version],
            'status': 'active' if not self.version_deprecation[version]['deprecated'] else 'deprecated'
        }
    
    def get_version_features(self, version: str) -> Dict[str, bool]:
        """Lấy danh sách tính năng của phiên bản"""
        if not self.is_version_supported(version):
            return {}
        
        return self.version_features[version]
    
    def mark_version_deprecated(self, version: str, deprecation_date: str, sunset_date: str, migration_guide: str = None):
        """Đánh dấu phiên bản là deprecated"""
        if version in self.version_deprecation:
            self.version_deprecation[version].update({
                'deprecated': True,
                'deprecation_date': deprecation_date,
                'sunset_date': sunset_date,
                'migration_guide': migration_guide
            })
            logger.warning(f"API version {version} marked as deprecated")
    
    def add_version_feature(self, version: str, feature: str, enabled: bool = True):
        """Thêm tính năng cho phiên bản"""
        if version in self.version_features:
            self.version_features[version][feature] = enabled
            logger.info(f"Feature '{feature}' {'enabled' if enabled else 'disabled'} for API version {version}")
    
    def get_version_compatibility(self, from_version: str, to_version: str) -> Dict[str, Any]:
        """Kiểm tra tính tương thích giữa các phiên bản"""
        if not self.is_version_supported(from_version) or not self.is_version_supported(to_version):
            return {
                'error': 'One or both versions are not supported',
                'supported_versions': self.supported_versions
            }
        
        from_features = self.version_features[from_version]
        to_features = self.version_features[to_version]
        
        # So sánh tính năng
        removed_features = []
        added_features = []
        unchanged_features = []
        
        for feature in from_features:
            if feature in to_features:
                if from_features[feature] == to_features[feature]:
                    unchanged_features.append(feature)
                else:
                    removed_features.append(feature)
            else:
                removed_features.append(feature)
        
        for feature in to_features:
            if feature not in from_features:
                added_features.append(feature)
        
        compatibility_score = len(unchanged_features) / len(from_features) * 100
        
        return {
            'from_version': from_version,
            'to_version': to_version,
            'compatibility_score': compatibility_score,
            'removed_features': removed_features,
            'added_features': added_features,
            'unchanged_features': unchanged_features,
            'migration_complexity': 'low' if compatibility_score > 80 else 'medium' if compatibility_score > 60 else 'high'
        }

class APIVersionMiddleware:
    """Middleware để xử lý API versioning"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.version_manager = APIVersionManager()
    
    def __call__(self, request):
        # Xác định phiên bản API từ URL hoặc header
        api_version = self._extract_api_version(request)
        
        if api_version:
            # Kiểm tra phiên bản có được hỗ trợ không
            if not self.version_manager.is_version_supported(api_version):
                return self._version_not_supported_response(api_version)
            
            # Thêm thông tin phiên bản vào request
            request.api_version = api_version
            request.version_info = self.version_manager.get_version_info(api_version)
            
            # Kiểm tra deprecated version
            if request.version_info.get('deprecated', False):
                self._add_deprecation_headers(request)
        
        response = self.get_response(request)
        
        # Thêm version headers vào response
        self._add_version_headers(response, request)
        
        return response
    
    def _extract_api_version(self, request) -> Optional[str]:
        """Trích xuất phiên bản API từ request"""
        # Kiểm tra từ URL path
        path_parts = request.path.split('/')
        if len(path_parts) > 2 and path_parts[1] == 'api':
            if len(path_parts) > 2 and path_parts[2].startswith('v'):
                return path_parts[2]
        
        # Kiểm tra từ header
        version_header = request.META.get('HTTP_X_API_VERSION')
        if version_header:
            return version_header
        
        # Kiểm tra từ query parameter
        version_param = request.GET.get('version')
        if version_param:
            return version_param
        
        # Trả về phiên bản mặc định
        return self.version_manager.get_default_version()
    
    def _version_not_supported_response(self, version: str):
        """Response khi phiên bản không được hỗ trợ"""
        from django.http import JsonResponse
        
        return JsonResponse({
            'error': f'API version {version} is not supported',
            'supported_versions': self.version_manager.get_supported_versions(),
            'default_version': self.version_manager.get_default_version(),
            'message': f'Please use one of the supported versions or upgrade to the latest version'
        }, status=400)
    
    def _add_deprecation_headers(self, request):
        """Thêm headers cảnh báo deprecated version"""
        version_info = request.version_info
        if version_info.get('deprecated'):
            # Thêm thông tin deprecated vào request để sử dụng trong views
            request.deprecation_warning = {
                'message': f'API version {request.api_version} is deprecated',
                'deprecation_date': version_info.get('deprecation_date'),
                'sunset_date': version_info.get('sunset_date'),
                'migration_guide': version_info.get('migration_guide')
            }
    
    def _add_version_headers(self, response, request):
        """Thêm version headers vào response"""
        if hasattr(request, 'api_version'):
            response['X-API-Version'] = request.api_version
            
            if hasattr(request, 'deprecation_warning'):
                response['X-API-Deprecated'] = 'true'
                response['X-API-Deprecation-Date'] = request.deprecation_warning.get('deprecation_date', '')
                response['X-API-Sunset-Date'] = request.deprecation_warning.get('sunset_date', '')
                if request.deprecation_warning.get('migration_guide'):
                    response['X-API-Migration-Guide'] = request.deprecation_warning['migration_guide']

# API Version Endpoints
@api_view(['GET'])
@permission_classes([AllowAny])
def api_versions_info(request):
    """Lấy thông tin về tất cả phiên bản API"""
    version_manager = APIVersionManager()
    
    versions_info = {}
    for version in version_manager.get_supported_versions():
        versions_info[version] = version_manager.get_version_info(version)
    
    return Response({
        'supported_versions': version_manager.get_supported_versions(),
        'default_version': version_manager.get_default_version(),
        'versions': versions_info,
        'current_version': getattr(request, 'api_version', 'unknown')
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def api_version_detail(request, version):
    """Lấy thông tin chi tiết về phiên bản API cụ thể"""
    version_manager = APIVersionManager()
    
    if not version_manager.is_version_supported(version):
        return Response({
            'error': f'Version {version} is not supported',
            'supported_versions': version_manager.get_supported_versions()
        }, status=400)
    
    version_info = version_manager.get_version_info(version)
    
    return Response(version_info)

@api_view(['GET'])
@permission_classes([AllowAny])
def api_version_compatibility(request, from_version, to_version):
    """Kiểm tra tính tương thích giữa hai phiên bản API"""
    version_manager = APIVersionManager()
    
    compatibility = version_manager.get_version_compatibility(from_version, to_version)
    
    if 'error' in compatibility:
        return Response(compatibility, status=400)
    
    return Response(compatibility)

# URL patterns cho API versioning
def get_versioned_urlpatterns(version: str):
    """Tạo URL patterns cho phiên bản cụ thể"""
    from . import views, admin_views, health_checks
    
    if version == 'v1':
        return [
            # V1 endpoints - cơ bản
            path('health/basic/', health_checks.health_check_basic, name='v1_health_basic'),
            path('health/detailed/', health_checks.health_check_detailed, name='v1_health_detailed'),
            path('health/providers/', health_checks.health_check_providers, name='v1_health_providers'),
            path('health/ready/', health_checks.health_check_ready, name='v1_health_ready'),
            
            # Admin endpoints
            path('admin/dashboard/', admin_views.admin_dashboard_data, name='v1_admin_dashboard'),
            path('admin/reference-odds/', admin_views.get_reference_odds, name='v1_admin_reference_odds'),
            path('admin/market-analysis/', admin_views.get_market_analysis, name='v1_admin_market_analysis'),
            path('admin/provider-markets/', admin_views.get_provider_markets, name='v1_admin_provider_markets'),
            path('admin/circuit-breaker-status/', admin_views.get_circuit_breaker_status, name='v1_admin_circuit_breaker_status'),
            path('admin/reset-circuit-breaker/', admin_views.reset_circuit_breaker, name='v1_admin_reset_circuit_breaker'),
            path('admin/active-conflicts/', admin_views.get_active_conflicts, name='v1_admin_active_conflicts'),
            path('admin/resolve-conflict/', admin_views.resolve_conflict_manually, name='v1_admin_resolve_conflict'),
            path('admin/alert-history/', admin_views.get_alert_history, name='v1_admin_alert_history'),
            path('admin/force-sync/', admin_views.force_sync_data, name='v1_admin_force_sync'),
            path('admin/provider-performance/', admin_views.get_provider_performance, name='v1_admin_provider_performance'),
            
            # Webhook endpoints
            path('webhook/event/', views.webhook_event_handler, name='v1_webhook_event_handler'),
            path('webhook/score/', views.live_score_update, name='v1_live_score_update'),
            
            # Match events
            path('matches/<int:match_id>/events/', views.match_events, name='v1_match_events'),
            path('events/create/', views.create_match_event, name='v1_create_match_event'),
        ]
    
    elif version == 'v2':
        return [
            # V2 endpoints - nâng cao
            path('health/basic/', health_checks.health_check_basic, name='v2_health_basic'),
            path('health/detailed/', health_checks.health_check_detailed, name='v2_health_detailed'),
            path('health/providers/', health_checks.health_check_providers, name='v2_health_providers'),
            path('health/ready/', health_checks.health_check_ready, name='v2_health_ready'),
            
            # V2 Admin endpoints với tính năng nâng cao
            path('admin/dashboard/', admin_views.admin_dashboard_data, name='v2_admin_dashboard'),
            path('admin/reference-odds/', admin_views.get_reference_odds, name='v2_admin_reference_odds'),
            path('admin/market-analysis/', admin_views.get_market_analysis, name='v2_admin_market_analysis'),
            path('admin/provider-markets/', admin_views.get_provider_markets, name='v2_admin_provider_markets'),
            path('admin/circuit-breaker-status/', admin_views.get_circuit_breaker_status, name='v2_admin_circuit_breaker_status'),
            path('admin/reset-circuit-breaker/', admin_views.reset_circuit_breaker, name='v2_admin_reset_circuit_breaker'),
            path('admin/active-conflicts/', admin_views.get_active_conflicts, name='v2_admin_active_conflicts'),
            path('admin/resolve-conflict/', admin_views.resolve_conflict_manually, name='v2_admin_resolve_conflict'),
            path('admin/alert-history/', admin_views.get_alert_history, name='v2_admin_alert_history'),
            path('admin/force-sync/', admin_views.force_sync_data, name='v2_admin_force_sync'),
            path('admin/provider-performance/', admin_views.get_provider_performance, name='v2_admin_provider_performance'),
            
            # V2 Webhook endpoints với validation nâng cao
            path('webhook/event/', views.webhook_event_handler, name='v2_webhook_event_handler'),
            path('webhook/score/', views.live_score_update, name='v2_live_score_update'),
            
            # V2 Match events với tính năng nâng cao
            path('matches/<int:match_id>/events/', views.match_events, name='v2_match_events'),
            path('events/create/', views.create_match_event, name='v2_create_match_event'),
            
            # V2 specific endpoints
            path('analytics/performance/', views.performance_analytics, name='v2_performance_analytics'),
            path('bulk/operations/', views.bulk_operations, name='v2_bulk_operations'),
        ]
    
    return []

# Global instance
api_version_manager = APIVersionManager()
