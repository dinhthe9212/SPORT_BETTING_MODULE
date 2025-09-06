"""
URL configuration for carousel_service_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from carousel.health_views import (
    HealthCheckView, ComprehensiveHealthView, MetricsView,
    ReadinessView, LivenessView
)
from carousel.analytics_views import (
    TrendingItemsView, AnalyticsDashboardView,
    user_behavior_analytics, conversion_analytics,
    public_analytics_summary, refresh_analytics_cache
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("carousel.urls")),
    
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    
    # Health check endpoints (FREE monitoring)
    path('health/', HealthCheckView.as_view(), name='health'),
    path('health/comprehensive/', ComprehensiveHealthView.as_view(), name='comprehensive_health'),
    path('health/ready/', ReadinessView.as_view(), name='readiness'),
    path('health/live/', LivenessView.as_view(), name='liveness'),
    path('metrics/', MetricsView.as_view(), name='metrics'),
    
    # Analytics endpoints (Rule-based, NO AI/ML)
    path('analytics/trending/', TrendingItemsView.as_view(), name='trending_items'),
    path('analytics/dashboard/', AnalyticsDashboardView.as_view(), name='analytics_dashboard'),
    path('analytics/user-behavior/', user_behavior_analytics, name='user_behavior_analytics'),
    path('analytics/conversion/', conversion_analytics, name='conversion_analytics'),
    path('analytics/public-summary/', public_analytics_summary, name='public_analytics'),
    path('analytics/refresh-cache/', refresh_analytics_cache, name='refresh_analytics_cache'),
]
