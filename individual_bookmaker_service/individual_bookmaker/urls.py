from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Router cho ViewSets
router = DefaultRouter()
router.register(r'bookmakers', views.IndividualBookmakerViewSet, basename='bookmaker')
router.register(r'tutorials', views.RiskEducationTutorialViewSet, basename='tutorial')
router.register(r'alerts', views.RiskAlertViewSet, basename='alert')
router.register(r'performance', views.BookmakerPerformanceViewSet, basename='performance')

# URL patterns
urlpatterns = [
    # Dashboard và Overview
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('risk-overview/', views.RiskOverviewView.as_view(), name='risk-overview'),
    path('performance/', views.PerformanceView.as_view(), name='performance'),
    
    # Education System
    path('education/', views.EducationView.as_view(), name='education'),
    
    # Alerts Management
    path('alerts/', views.AlertsView.as_view(), name='alerts'),
    
    # Best Practices
    path('best-practices/', views.BestPracticesView.as_view(), name='best-practices'),
    
    # Webhook và Integration
    path('webhook/risk-update/', views.webhook_risk_update, name='webhook-risk-update'),
    
    # Health Check
    path('health/', views.health_check, name='health-check'),
    
    # Include router URLs
    path('', include(router.urls)),
]

# API versioning (nếu cần)
api_v1_patterns = [
    path('v1/', include(urlpatterns)),
]

# Root URL patterns
root_patterns = [
    path('api/', include(urlpatterns)),
    path('api/v1/', include(api_v1_patterns)),
]
