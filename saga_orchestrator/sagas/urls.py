from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'transactions', views.SagaTransactionViewSet)
router.register(r'definitions', views.SagaDefinitionViewSet)
router.register(r'events', views.SagaEventViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('start/', views.start_saga, name='start_saga'),
    path('statistics/', views.saga_statistics, name='saga_statistics'),
    path('health/', views.health_check, name='health_check'),
    
    # ============================================================================
    # CASH OUT SAGA ENDPOINTS
    # ============================================================================
    path('cashout/start/', views.start_cashout_saga, name='start_cashout_saga'),
    path('cashout/rollback/', views.rollback_cashout_saga, name='rollback_cashout_saga'),
    path('cashout/status/<str:saga_id>/', views.get_cashout_saga_status, name='get_cashout_saga_status'),
    path('cashout/list/', views.list_cashout_sagas, name='list_cashout_sagas'),
    path('cashout/<str:saga_id>/retry/<str:step_name>/', views.retry_cashout_saga_step, name='retry_cashout_saga_step'),
]

