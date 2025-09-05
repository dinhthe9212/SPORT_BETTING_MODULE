from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Tạo router cho ViewSets
router = DefaultRouter()
router.register(r'sports', views.SportViewSet)
router.register(r'teams', views.TeamViewSet)
router.register(r'matches', views.MatchViewSet)
router.register(r'bet-types', views.BetTypeViewSet)
router.register(r'odds', views.OddViewSet)
router.register(r'bet-slips', views.BetSlipViewSet)
router.register(r'bet-selections', views.BetSelectionViewSet)
router.register(r'bet-slip-purchases', views.BetSlipPurchaseViewSet)
router.register(r'responsible-gaming-policies', views.ResponsibleGamingPolicyViewSet)
router.register(r'user-activity-logs', views.UserActivityLogViewSet)

# Leaderboard & Statistics URLs
router.register(r'user-statistics', views.UserStatisticsViewSet, basename='user-statistics')
router.register(r'leaderboard', views.LeaderboardViewSet, basename='leaderboard')
router.register(r'betting-statistics', views.BettingStatisticsViewSet, basename='betting-statistics')
router.register(r'performance-metrics', views.PerformanceMetricsViewSet, basename='performance-metrics')

# P2P Marketplace & Fractional Ownership URLs
router.register(r'bet-slip-ownerships', views.BetSlipOwnershipViewSet, basename='bet-slip-ownerships')
router.register(r'order-book', views.OrderBookViewSet, basename='order-book')
router.register(r'market-suspensions', views.MarketSuspensionViewSet, basename='market-suspensions')
router.register(r'trading-sessions', views.TradingSessionViewSet, basename='trading-sessions')
router.register(r'p2p-transactions', views.P2PTransactionViewSet, basename='p2p-transactions')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # ============================================================================
    # ODDS MANAGEMENT ENDPOINTS
    # ============================================================================
    
    # Odds Information
    path('matches/<int:match_id>/odds/', views.get_odds_for_match, name='get_odds_for_match'),
    path('odds/<int:odd_id>/history/', views.get_odds_history, name='get_odds_history'),
    path('matches/<int:match_id>/odds/significant-changes/', views.get_significant_odds_changes, name='get_significant_odds_changes'),
    path('matches/<int:match_id>/odds/analytics/', views.get_odds_analytics, name='get_odds_analytics'),
    path('matches/<int:match_id>/odds/snapshot/', views.get_odds_snapshot, name='get_odds_snapshot'),
    
    # Odds Management (Admin only)
    path('odds/<int:odd_id>/adjust/', views.adjust_odds_manually, name='adjust_odds_manually'),
    path('matches/<int:match_id>/odds/suspend/', views.suspend_odds_for_match, name='suspend_odds_for_match'),
    path('matches/<int:match_id>/odds/resume/', views.resume_odds_for_match, name='resume_odds_for_match'),
    path('matches/<int:match_id>/odds/update-risk/', views.update_odds_for_risk, name='update_odds_for_risk'),
    
    # ============================================================================
    # RISK INTEGRATION ENDPOINTS
    # ============================================================================
    
    path('odds/<int:odd_id>/risk-profile/', views.get_risk_profile_for_odds, name='get_risk_profile_for_odds'),
    path('odds/<int:odd_id>/configure-risk/', views.configure_risk_based_odds, name='configure_risk_based_odds'),
    
    # ============================================================================
    # CASH OUT ENDPOINTS
    # ============================================================================
    
    # Cash Out Configuration Management
    path('cashout/configurations/', views.CashOutConfigurationViewSet.as_view({
        'get': 'list',
        'post': 'create'
    }), name='cashout_config_list'),
    path('cashout/configurations/<int:pk>/', views.CashOutConfigurationViewSet.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'
    }), name='cashout_config_detail'),
    
    # Cash Out History
    path('cashout/history/', views.CashOutHistoryViewSet.as_view({
        'get': 'list'
    }), name='cashout_history_list'),
    path('cashout/history/<int:pk>/', views.CashOutHistoryViewSet.as_view({
        'get': 'retrieve'
    }), name='cashout_history_detail'),
    
    # Cash Out Operations
    path('cashout/request-quote/', views.CashOutViewSet.as_view({
        'post': 'request_quote'
    }), name='cashout_request_quote'),
    path('cashout/confirm/', views.CashOutViewSet.as_view({
        'post': 'confirm_cash_out'
    }), name='cashout_confirm'),
    path('cashout/check-eligibility/', views.CashOutViewSet.as_view({
        'get': 'check_eligibility'
    }), name='cashout_check_eligibility'),

    # Market suspension endpoints
    path('webhook/sports/', views.sports_webhook_handler, name='sports_webhook_handler'),
    path('matches/<int:match_id>/market-suspension/status/', views.market_suspension_status, name='market_suspension_status'),
    path('matches/<int:match_id>/market-suspension/suspend/', views.manual_market_suspension, name='manual_market_suspension'),
    path('matches/<int:match_id>/market-suspension/resume/', views.resume_market_manually, name='resume_market_manually'),
    
    # ============================================================================
    # AUTO ORDER MANAGEMENT ENDPOINTS (Chốt Lời & Cắt Lỗ tự động)
    # ============================================================================
    
    # Auto Order Setup & Management
    path('auto-orders/setup/', views.setup_auto_order, name='setup_auto_order'),
    path('auto-orders/cancel/', views.cancel_auto_order, name='cancel_auto_order'),
    path('auto-orders/status/<int:bet_slip_id>/', views.get_auto_order_status, name='get_auto_order_status'),
    path('auto-orders/user/', views.get_user_auto_orders, name='get_user_auto_orders'),
    
    # Auto Order Statistics & Monitoring (Admin only)
    path('auto-orders/statistics/', views.get_auto_order_statistics, name='get_auto_order_statistics'),
    path('auto-orders/monitoring/start/', views.start_auto_monitoring, name='start_auto_monitoring'),
]


