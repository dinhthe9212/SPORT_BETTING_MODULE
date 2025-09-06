from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    LiabilityCalculationViewSet, VigorishMarginViewSet, RiskThresholdViewSet,
    PromotionRiskViewSet, InPlayRiskViewSet, BookmakerRoleViewSet,
    RiskManagementOrchestratorViewSet, PerformanceOptimizationViewSet,
    AutomatedWorkflowViewSet, PerformanceMetricsViewSet,
    RiskAdjustedOddsAPIView, BatchRiskAdjustedOddsAPIView, RiskAdjustedOddsTestAPIView
)

# Tạo router cho các ViewSets
router = DefaultRouter()
router.register(r'price-volatility', views.PriceVolatilityViewSet)
router.register(r'market-activity', views.MarketActivityViewSet)
router.register(r'trading-suspensions', views.TradingSuspensionViewSet)
router.register(r'risk-configs', views.RiskConfigurationViewSet)
router.register(r'risk-alerts', views.RiskAlertViewSet)
router.register(r'risk-metrics', views.RiskMetricsViewSet)
router.register(r'audit-logs', views.RiskAuditLogViewSet)
router.register(r'risk-check', views.RiskCheckViewSet, basename='risk-check')

# Performance Optimization URLs
router.register(r'performance-optimization', PerformanceOptimizationViewSet, basename='performance-optimization')

# Automated Workflows URLs
router.register(r'automated-workflows', AutomatedWorkflowViewSet, basename='automated-workflows')

# Performance Metrics URLs
router.register(r'performance-metrics', PerformanceMetricsViewSet, basename='performance-metrics')

# Thêm các ViewSet mới
router.register(r'liability-calculation', LiabilityCalculationViewSet, basename='liability-calculation')
router.register(r'vigorish-margin', VigorishMarginViewSet, basename='vigorish-margin')
router.register(r'risk-threshold', RiskThresholdViewSet, basename='risk-threshold')
router.register(r'promotion-risk', PromotionRiskViewSet, basename='promotion-risk')
router.register(r'inplay-risk', InPlayRiskViewSet, basename='inplay-risk')
router.register(r'bookmaker-role', BookmakerRoleViewSet, basename='bookmaker-role')
router.register(r'risk-orchestrator', RiskManagementOrchestratorViewSet, basename='risk-orchestrator')

# URL patterns
urlpatterns = [
    # Dashboard
    path('dashboard/', views.RiskDashboardView.as_view(), name='risk-dashboard'),
    
    # Risk-Adjusted Offered Odds APIs
    path('risk-adjusted-odds/', RiskAdjustedOddsAPIView.as_view(), name='risk-adjusted-odds'),
    path('risk-adjusted-odds/batch/', BatchRiskAdjustedOddsAPIView.as_view(), name='batch-risk-adjusted-odds'),
    path('risk-adjusted-odds/test/', RiskAdjustedOddsTestAPIView.as_view(), name='test-risk-adjusted-odds'),
    
    # Include router URLs
    path('', include(router.urls)),
]

# API endpoints tổng quan:
# 
# Price Volatility Monitoring:
# - GET /api/v1/risk/price-volatility/ - Lấy danh sách monitor biến động giá
# - POST /api/v1/risk/price-volatility/check_volatility/ - Kiểm tra biến động giá
# - GET /api/v1/risk/price-volatility/stats/ - Thống kê biến động giá
# 
# Market Activity Monitoring:
# - GET /api/v1/risk/market-activity/ - Lấy danh sách hoạt động thị trường
# - POST /api/v1/risk/market-activity/detect_unusual_volume/ - Phát hiện volume bất thường
# - POST /api/v1/risk/market-activity/detect_rapid_price_changes/ - Phát hiện thay đổi giá nhanh
# - POST /api/v1/risk/market-activity/detect_high_frequency_trading/ - Phát hiện giao dịch tần số cao
# - POST /api/v1/risk/market-activity/detect_large_order/ - Phát hiện lệnh lớn
# 
# Trading Suspension Management:
# - GET /api/v1/risk/trading-suspensions/ - Lấy danh sách tạm dừng
# - POST /api/v1/risk/trading-suspensions/create_suspension/ - Tạo tạm dừng giao dịch
# - POST /api/v1/risk/trading-suspensions/{id}/lift_suspension/ - Dỡ bỏ tạm dừng
# - POST /api/v1/risk/trading-suspensions/check_trading_allowed/ - Kiểm tra giao dịch được phép
# - GET /api/v1/risk/trading-suspensions/active_suspensions/ - Lấy tạm dừng đang hoạt động
# 
# Risk Configuration:
# - GET /api/v1/risk/risk-configs/ - Lấy cấu hình rủi ro
# - PATCH /api/v1/risk/risk-configs/{id}/update_config/ - Cập nhật cấu hình
# 
# Risk Alerts:
# - GET /api/v1/risk/risk-alerts/ - Lấy danh sách cảnh báo
# - POST /api/v1/risk/risk-alerts/{id}/acknowledge/ - Xác nhận cảnh báo
# - POST /api/v1/risk/risk-alerts/{id}/resolve/ - Giải quyết cảnh báo
# 
# Risk Metrics:
# - GET /api/v1/risk/risk-metrics/ - Lấy metrics rủi ro
# 
# Audit Logs:
# - GET /api/v1/risk/audit-logs/ - Lấy audit logs
# 
# Risk Dashboard:
# - GET /api/v1/risk/dashboard/ - Tổng quan dashboard
# - GET /api/v1/risk/dashboard/recent_activities/ - Hoạt động gần đây