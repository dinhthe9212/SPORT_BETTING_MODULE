from django.urls import path, include
from . import views
from . import admin_views
from . import health_checks
from . import api_versioning

urlpatterns = [
    # API Versioning endpoints
    path('versions/', api_versioning.api_versions_info, name='api_versions_info'),
    path('versions/<str:version>/', api_versioning.api_version_detail, name='api_version_detail'),
    path('versions/<str:from_version>/compatibility/<str:to_version>/', api_versioning.api_version_compatibility, name='api_version_compatibility'),
    
    # Health Check endpoints
    path('health/basic/', health_checks.health_check_basic, name='health_check_basic'),
    path('health/detailed/', health_checks.health_check_detailed, name='health_check_detailed'),
    path('health/providers/', health_checks.health_check_providers, name='health_check_providers'),
    path('health/ready/', health_checks.health_check_ready, name='health_check_ready'),
    
    # Webhook endpoints
    path('webhook/event/', views.webhook_event_handler, name='webhook_event_handler'),
    path('webhook/score/', views.live_score_update, name='live_score_update'),
    
    # Match events
    path('matches/<int:match_id>/events/', views.match_events, name='match_events'),
    path('events/create/', views.create_match_event, name='create_match_event'),
    
    # Admin endpoints
    path('admin/dashboard/', admin_views.admin_dashboard_data, name='admin_dashboard'),
    path('admin/reference-odds/', admin_views.get_reference_odds, name='admin_reference_odds'),
    path('admin/market-analysis/', admin_views.get_market_analysis, name='admin_market_analysis'),
    path('admin/provider-markets/', admin_views.get_provider_markets, name='admin_provider_markets'),
    path('admin/circuit-breaker-status/', admin_views.get_circuit_breaker_status, name='admin_circuit_breaker_status'),
    path('admin/reset-circuit-breaker/', admin_views.reset_circuit_breaker, name='admin_reset_circuit_breaker'),
    path('admin/active-conflicts/', admin_views.get_active_conflicts, name='admin_active_conflicts'),
    path('admin/resolve-conflict/', admin_views.resolve_conflict_manually, name='admin_resolve_conflict'),
    path('admin/alert-history/', admin_views.get_alert_history, name='admin_alert_history'),
    path('admin/force-sync/', admin_views.force_sync_data, name='admin_force_sync'),
    path('admin/provider-performance/', admin_views.get_provider_performance, name='admin_provider_performance'),
]

# Versioned URL patterns
urlpatterns += [
    # V1 API endpoints
    path('v1/', include(api_versioning.get_versioned_urlpatterns('v1'))),
    
    # V2 API endpoints
    path('v2/', include(api_versioning.get_versioned_urlpatterns('v2'))),
]


