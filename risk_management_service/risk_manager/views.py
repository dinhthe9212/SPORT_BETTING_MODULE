from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from decimal import Decimal

from .models import (
    PriceVolatilityMonitor, MarketActivityMonitor, TradingSuspension,
    RiskConfiguration, RiskAlert, RiskMetrics, RiskAuditLog
)
from .serializers import (
    PriceVolatilityMonitorSerializer, MarketActivityMonitorSerializer, TradingSuspensionSerializer,
    RiskConfigurationSerializer, RiskAlertSerializer, RiskMetricsSerializer, RiskAuditLogSerializer,
    PriceVolatilityCheckSerializer, TradingSuspensionCreateSerializer, TradingCheckSerializer,
    TradingCheckResponseSerializer, UnusualVolumeDetectionSerializer,
    RapidPriceChangeDetectionSerializer, HighFrequencyTradingDetectionSerializer, LargeOrderDetectionSerializer,
    AlertAcknowledgeSerializer, AlertResolveSerializer, DashboardSummarySerializer, RecentActivitySerializer,
    VolatilityStatsSerializer, ConfigurationUpdateSerializer
)
from .services import (
    PriceVolatilityService, MarketActivityService, TradingSuspensionService, RiskDashboardService, RiskCheckService, LiveOddsService, EventMarginService,
    LiabilityCalculationService, VigorishMarginService, RiskThresholdService,
    PromotionRiskService, InPlayRiskService, BookmakerRoleManagementService,
    RiskManagementOrchestratorService, RiskAdjustedOddsService
)
from .performance_optimizer import PerformanceOptimizer
from .automated_workflows import AutomatedWorkflowService
from .performance_metrics import PerformanceMetricsService

# ============================================================================
# P2P MARKETPLACE RISK MANAGEMENT VIEWS
# ============================================================================

class PriceVolatilityViewSet(viewsets.ModelViewSet):
    """API quản lý theo dõi biến động giá"""
    queryset = PriceVolatilityMonitor.objects.all()
    serializer_class = PriceVolatilityMonitorSerializer
    permission_classes = []  # Tạm thời tắt permission để test
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by bet_slip_id
        bet_slip_id = self.request.query_params.get('bet_slip_id')
        if bet_slip_id:
            queryset = queryset.filter(bet_slip_id=bet_slip_id)
        
        # Filter by severity
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity_level=severity)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(detection_time__gte=date_from)
        if date_to:
            queryset = queryset.filter(detection_time__lte=date_to)
        
        return queryset.order_by('-detection_time')
    
    @action(detail=False, methods=['post'])
    def check_volatility(self, request):
        """Kiểm tra biến động giá"""
        serializer = PriceVolatilityCheckSerializer(data=request.data)
        if serializer.is_valid():
            service = PriceVolatilityService()
            monitor = service.monitor_price_change(
                bet_slip_id=serializer.validated_data['bet_slip_id'],
                market_identifier=serializer.validated_data['market_identifier'],
                original_price=serializer.validated_data['original_price'],
                current_price=serializer.validated_data['current_price']
            )
            
            if monitor:
                return Response({
                    'success': True,
                    'message': 'Price volatility monitored',
                    'monitor_id': str(monitor.id),
                    'severity': monitor.severity_level,
                    'price_change_percentage': float(monitor.price_change_percentage)
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': False,
                    'message': 'Failed to monitor price volatility'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Lấy thống kê biến động giá"""
        hours = int(request.query_params.get('hours', 24))
        service = PriceVolatilityService()
        stats = service.get_volatility_stats(hours)
        
        serializer = VolatilityStatsSerializer(stats)
        return Response(serializer.data)

class MarketActivityViewSet(viewsets.ModelViewSet):
    """API quản lý theo dõi hoạt động thị trường"""
    queryset = MarketActivityMonitor.objects.all()
    serializer_class = MarketActivityMonitorSerializer
    permission_classes = []  # Tạm thời tắt permission để test
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by activity_type
        activity_type = self.request.query_params.get('activity_type')
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        # Filter by user_id
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by severity
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity_level=severity)
        
        return queryset.order_by('-detected_at')
    
    @action(detail=False, methods=['post'])
    def detect_unusual_volume(self, request):
        """Phát hiện volume bất thường"""
        serializer = UnusualVolumeDetectionSerializer(data=request.data)
        if serializer.is_valid():
            service = MarketActivityService()
            monitor = service.detect_unusual_volume(
                market_identifier=serializer.validated_data['market_identifier'],
                current_volume=serializer.validated_data['current_volume'],
                historical_average=serializer.validated_data['historical_average']
            )
            
            if monitor:
                return Response({
                    'success': True,
                    'message': 'Unusual volume detected',
                    'monitor_id': str(monitor.id),
                    'severity': monitor.severity_level
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': True,
                    'message': 'Volume is within normal range'
                }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def detect_rapid_price_changes(self, request):
        """Phát hiện thay đổi giá nhanh"""
        serializer = RapidPriceChangeDetectionSerializer(data=request.data)
        if serializer.is_valid():
            service = MarketActivityService()
            monitor = service.detect_rapid_price_changes(
                market_identifier=serializer.validated_data['market_identifier'],
                price_changes=serializer.validated_data['price_changes']
            )
            
            if monitor:
                return Response({
                    'success': True,
                    'message': 'Rapid price changes detected',
                    'monitor_id': str(monitor.id),
                    'severity': monitor.severity_level
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': True,
                    'message': 'Price changes are within normal range'
                }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def detect_high_frequency_trading(self, request):
        """Phát hiện giao dịch tần số cao"""
        serializer = HighFrequencyTradingDetectionSerializer(data=request.data)
        if serializer.is_valid():
            service = MarketActivityService()
            monitor = service.detect_high_frequency_trading(
                user_id=serializer.validated_data['user_id'],
                market_identifier=serializer.validated_data['market_identifier'],
                recent_orders=serializer.validated_data['recent_orders']
            )
            
            if monitor:
                return Response({
                    'success': True,
                    'message': 'High frequency trading detected',
                    'monitor_id': str(monitor.id),
                    'severity': monitor.severity_level
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': True,
                    'message': 'Trading frequency is within normal range'
                }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def detect_large_order(self, request):
        """Phát hiện lệnh lớn"""
        serializer = LargeOrderDetectionSerializer(data=request.data)
        if serializer.is_valid():
            service = MarketActivityService()
            monitor = service.detect_large_orders(
                user_id=serializer.validated_data['user_id'],
                market_identifier=serializer.validated_data['market_identifier'],
                order_amount=serializer.validated_data['order_amount']
            )
            
            if monitor:
                return Response({
                    'success': True,
                    'message': 'Large order detected',
                    'monitor_id': str(monitor.id),
                    'severity': monitor.severity_level
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'success': True,
                    'message': 'Order size is within normal range'
                }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TradingSuspensionViewSet(viewsets.ModelViewSet):
    """API quản lý tạm dừng giao dịch"""
    queryset = TradingSuspension.objects.all()
    serializer_class = TradingSuspensionSerializer
    permission_classes = []  # Tạm thời tắt permission để test
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by suspension_type
        suspension_type = self.request.query_params.get('suspension_type')
        if suspension_type:
            queryset = queryset.filter(suspension_type=suspension_type)
        
        return queryset.order_by('-suspended_at')
    
    @action(detail=False, methods=['post'])
    def create_suspension(self, request):
        """Tạo tạm dừng giao dịch"""
        serializer = TradingSuspensionCreateSerializer(data=request.data)
        if serializer.is_valid():
            service = TradingSuspensionService()
            suspension = service.suspend_trading(
                suspension_type=serializer.validated_data['suspension_type'],
                reason=serializer.validated_data['reason'],
                description=serializer.validated_data['description'],
                suspended_by='admin',  # Tạm thời hardcode
                sport_id=serializer.validated_data.get('sport_id'),
                market_identifier=serializer.validated_data.get('market_identifier'),
                user_id=serializer.validated_data.get('user_id'),
                event_id=serializer.validated_data.get('event_id'),
                expires_at=serializer.validated_data.get('expires_at')
            )
            
            return Response({
                'success': True,
                'message': 'Trading suspension created',
                'suspension_id': str(suspension.id)
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def lift_suspension(self, request, pk=None):
        """Dỡ bỏ tạm dừng giao dịch"""
        service = TradingSuspensionService()
        success = service.lift_suspension(
            suspension_id=pk,
            lifted_by='admin'  # Tạm thời hardcode
        )
        
        if success:
            return Response({
                'success': True,
                'message': 'Trading suspension lifted'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Failed to lift suspension'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def check_trading_allowed(self, request):
        """Kiểm tra giao dịch có được phép không"""
        serializer = TradingCheckSerializer(data=request.data)
        if serializer.is_valid():
            service = TradingSuspensionService()
            allowed, reason = service.check_trading_allowed(
                user_id=serializer.validated_data.get('user_id'),
                sport_id=serializer.validated_data.get('sport_id'),
                market_identifier=serializer.validated_data.get('market_identifier'),
                event_id=serializer.validated_data.get('event_id')
            )
            
            response_data = TradingCheckResponseSerializer({
                'allowed': allowed,
                'reason': reason
            }).data
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def active_suspensions(self, request):
        """Lấy danh sách tạm dừng đang hoạt động"""
        service = TradingSuspensionService()
        suspensions = service.get_active_suspensions()
        
        return Response({
            'success': True,
            'suspensions': suspensions
        }, status=status.HTTP_200_OK)

class RiskConfigurationViewSet(viewsets.ModelViewSet):
    """API quản lý cấu hình rủi ro"""
    queryset = RiskConfiguration.objects.all()
    serializer_class = RiskConfigurationSerializer
    permission_classes = []  # Tạm thời tắt permission để test
    
    @action(detail=True, methods=['patch'])
    def update_config(self, request, pk=None):
        """Cập nhật cấu hình"""
        try:
            config = self.get_object()
            serializer = ConfigurationUpdateSerializer(data=request.data)
            
            if serializer.is_valid():
                config.config_value = serializer.validated_data['config_value']
                if 'description' in serializer.validated_data:
                    config.description = serializer.validated_data['description']
                config.updated_by = serializer.validated_data['updated_by']
                config.save()
                
                return Response({
                    'success': True,
                    'message': 'Configuration updated'
                }, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except RiskConfiguration.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Configuration not found'
            }, status=status.HTTP_404_NOT_FOUND)

class RiskAlertViewSet(viewsets.ModelViewSet):
    """API quản lý cảnh báo rủi ro"""
    queryset = RiskAlert.objects.all()
    serializer_class = RiskAlertSerializer
    permission_classes = []  # Tạm thời tắt permission để test
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by severity
        severity = self.request.query_params.get('severity')
        if severity:
            queryset = queryset.filter(severity=severity)
        
        # Filter by alert_type
        alert_type = self.request.query_params.get('alert_type')
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Xác nhận cảnh báo"""
        try:
            alert = self.get_object()
            serializer = AlertAcknowledgeSerializer(data=request.data)
            
            if serializer.is_valid():
                alert.acknowledge(serializer.validated_data['acknowledged_by'])
                
                return Response({
                    'success': True,
                    'message': 'Alert acknowledged'
                }, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except RiskAlert.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Alert not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Giải quyết cảnh báo"""
        try:
            alert = self.get_object()
            serializer = AlertResolveSerializer(data=request.data)
            
            if serializer.is_valid():
                alert.resolve(
                    resolved_by=serializer.validated_data['resolved_by'],
                    resolution_notes=serializer.validated_data.get('resolution_notes', '')
                )
                
                return Response({
                    'success': True,
                    'message': 'Alert resolved'
                }, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except RiskAlert.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Alert not found'
            }, status=status.HTTP_404_NOT_FOUND)

class RiskMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """API xem metrics rủi ro"""
    queryset = RiskMetrics.objects.all()
    serializer_class = RiskMetricsSerializer
    permission_classes = []  # Tạm thời tắt permission để test
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by metric_type
        metric_type = self.request.query_params.get('metric_type')
        if metric_type:
            queryset = queryset.filter(metric_type=metric_type)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(timestamp__gte=date_from)
        if date_to:
            queryset = queryset.filter(timestamp__lte=date_to)
        
        return queryset.order_by('-timestamp')

class RiskAuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API xem audit log rủi ro"""
    queryset = RiskAuditLog.objects.all()
    serializer_class = RiskAuditLogSerializer
    permission_classes = []  # Tạm thời tắt permission để test
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by action_type
        action_type = self.request.query_params.get('action_type')
        if action_type:
            queryset = queryset.filter(action_type=action_type)
        
        # Filter by user_id
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        return queryset.order_by('-timestamp')

class RiskDashboardView(APIView):
    """API dashboard rủi ro"""
    permission_classes = []  # Tạm thời tắt permission để test
    
    def get(self, request):
        """Lấy tổng quan dashboard"""
        hours = int(request.query_params.get('hours', 24))
        service = RiskDashboardService()
        
        summary = service.get_dashboard_summary(hours)
        serializer = DashboardSummarySerializer(summary)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def recent_activities(self, request):
        """Lấy hoạt động gần đây"""
        limit = int(request.query_params.get('limit', 50))
        service = RiskDashboardService()
        
        activities = service.get_recent_activities(limit)
        serializer = RecentActivitySerializer(activities, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)

class PerformanceOptimizationViewSet(viewsets.ViewSet):
    """API endpoints cho Performance Optimization"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.optimizer = PerformanceOptimizer()
    
    @action(detail=False, methods=['get'])
    def optimize_database(self, request):
        """Tối ưu hóa database"""
        try:
            result = self.optimizer.optimize_database_queries()
            return Response({
                'status': 'success',
                'message': 'Database optimization completed',
                'result': result
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def implement_caching(self, request):
        """Implement caching strategy"""
        try:
            result = self.optimizer.implement_caching_strategy()
            return Response({
                'status': 'success',
                'message': 'Caching strategy implemented',
                'result': result
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def optimize_real_time(self, request):
        """Tối ưu hóa real-time processing"""
        try:
            result = self.optimizer.optimize_real_time_processing()
            return Response({
                'status': 'success',
                'message': 'Real-time processing optimization completed',
                'result': result
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def get_metrics(self, request):
        """Lấy performance metrics"""
        try:
            result = self.optimizer.get_performance_metrics()
            return Response({
                'status': 'success',
                'result': result
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def run_full_optimization(self, request):
        """Chạy toàn bộ optimization"""
        try:
            result = self.optimizer.run_full_optimization()
            return Response({
                'status': 'success',
                'message': 'Full optimization completed',
                'result': result
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)

class AutomatedWorkflowViewSet(viewsets.ViewSet):
    """API endpoints cho Automated Workflows"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.workflow_service = AutomatedWorkflowService()
    
    @action(detail=False, methods=['post'])
    def execute_workflow(self, request):
        """Thực thi workflow cụ thể"""
        try:
            workflow_name = request.data.get('workflow_name')
            event_data = request.data.get('event_data', {})
            
            if not workflow_name:
                return Response({
                    'status': 'error',
                    'message': 'workflow_name is required'
                }, status=400)
            
            result = self.workflow_service.execute_workflow(workflow_name, event_data)
            return Response({
                'status': 'success',
                'result': result
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    @action(detail=False, methods=['post'])
    def auto_detect_and_execute(self, request):
        """Tự động phát hiện và thực thi workflow"""
        try:
            event_data = request.data.get('event_data', {})
            
            if not event_data:
                return Response({
                    'status': 'error',
                    'message': 'event_data is required'
                }, status=400)
            
            result = self.workflow_service.auto_detect_and_execute_workflow(event_data)
            return Response({
                'status': 'success',
                'result': result
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def get_workflow_status(self, request):
        """Lấy trạng thái workflow execution"""
        try:
            execution_id = request.query_params.get('execution_id')
            
            if not execution_id:
                return Response({
                    'status': 'error',
                    'message': 'execution_id is required'
                }, status=400)
            
            result = self.workflow_service.get_workflow_status(execution_id)
            
            if result:
                return Response({
                    'status': 'success',
                    'result': result
                })
            else:
                return Response({
                    'status': 'error',
                    'message': 'Workflow execution not found'
                }, status=404)
                
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def get_workflow_history(self, request):
        """Lấy lịch sử workflow executions"""
        try:
            limit = int(request.query_params.get('limit', 50))
            result = self.workflow_service.get_workflow_history(limit)
            
            return Response({
                'status': 'success',
                'result': result
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    @action(detail=False, methods=['post'])
    def escalate_critical_risks(self, request):
        """Escalate rủi ro critical"""
        try:
            risk_level = request.data.get('risk_level', 'CRITICAL')
            result = self.workflow_service.escalate_critical_risks(risk_level)
            
            return Response({
                'status': 'success',
                'result': result
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    @action(detail=False, methods=['post'])
    def auto_notify_stakeholders(self, request):
        """Tự động thông báo stakeholders"""
        try:
            risk_event = request.data.get('risk_event', {})
            
            if not risk_event:
                return Response({
                    'status': 'error',
                    'message': 'risk_event is required'
                }, status=400)
            
            result = self.workflow_service.auto_notify_stakeholders(risk_event)
            return Response({
                'status': 'success',
                'result': result
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)

class PerformanceMetricsViewSet(viewsets.ViewSet):
    """API endpoints cho Performance Metrics"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.metrics_service = PerformanceMetricsService()
    
    @action(detail=False, methods=['get'])
    def get_overview(self, request):
        """Lấy tổng quan hiệu suất hệ thống"""
        try:
            hours = int(request.query_params.get('hours', 24))
            result = self.metrics_service.get_system_performance_overview(hours)
            
            return Response({
                'status': 'success',
                'result': result
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def get_trends(self, request):
        """Lấy xu hướng hiệu suất"""
        try:
            days = int(request.query_params.get('days', 7))
            result = self.metrics_service.get_performance_trends(days)
            
            return Response({
                'status': 'success',
                'result': result
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def get_recommendations(self, request):
        """Lấy khuyến nghị cải thiện hiệu suất"""
        try:
            result = self.metrics_service.get_performance_recommendations()
            
            return Response({
                'status': 'success',
                'result': result
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def export_report(self, request):
        """Xuất báo cáo hiệu suất"""
        try:
            format_type = request.query_params.get('format', 'json')
            result = self.metrics_service.export_performance_report(format_type)
            
            if 'error' in result:
                return Response({
                    'status': 'error',
                    'message': result['error']
                }, status=500)
            
            return Response({
                'status': 'success',
                'result': result
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=500)

class RiskCheckViewSet(viewsets.ViewSet):
    """API kiểm tra rủi ro cho betting operations"""
    permission_classes = []  # Tạm thời tắt permission để test
    
    @action(detail=False, methods=['post'])
    def check_bet(self, request):
        """Kiểm tra rủi ro của một bet trước khi chấp nhận"""
        try:
            bet_data = request.data
            required_fields = ['user_id', 'match_id', 'bet_type_id', 'outcome', 'stake_amount', 'odds_value']
            
            # Validate required fields
            for field in required_fields:
                if field not in bet_data:
                    return Response({
                        'error': f'Missing required field: {field}',
                        'approved': False
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Gọi service để kiểm tra rủi ro
            risk_service = RiskCheckService()
            risk_result = risk_service.check_bet_risk(bet_data)
            
            return Response(risk_result, status=status.HTTP_200_OK)
            
        except Exception as e:
            # logger.error(f"Error in check_bet: {str(e)}") # Original code had this line commented out
            return Response({
                'error': 'Internal server error during risk check',
                'approved': False
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def get_live_odds(self, request):
        """Lấy live odds cho cash out"""
        try:
            odds_request = request.data
            required_fields = ['match_id', 'bet_type_id', 'outcome']
            
            for field in required_fields:
                if field not in odds_request:
                    return Response({
                        'error': f'Missing required field: {field}'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            odds_service = LiveOddsService()
            live_odds = odds_service.get_live_odds(odds_request)
            
            return Response(live_odds, status=status.HTTP_200_OK)
            
        except Exception as e:
            # logger.error(f"Error in get_live_odds: {str(e)}") # Original code had this line commented out
            return Response({
                'error': 'Internal server error getting live odds'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['post'])
    def get_event_margin(self, request):
        """Lấy event margin cho cash out"""
        try:
            margin_request = request.data
            if 'match_id' not in margin_request:
                return Response({
                    'error': 'Missing match_id field'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            margin_service = EventMarginService()
            margin_info = margin_service.get_event_margin(margin_request['match_id'])
            
            return Response(margin_info, status=status.HTTP_200_OK)
            
        except Exception as e:
            # logger.error(f"Error in get_event_margin: {str(e)}") # Original code had this line commented out
            return Response({
                'error': 'Internal server error getting event margin'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class LiabilityCalculationViewSet(viewsets.ViewSet):
    """ViewSet cho tính toán Trách Nhiệm RÒNG"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.liability_service = LiabilityCalculationService()
    
    @action(detail=False, methods=['post'])
    def calculate_net_liability(self, request):
        """Tính toán Trách Nhiệm RÒNG cho một match"""
        try:
            match_id = request.data.get('match_id')
            bet_type_id = request.data.get('bet_type_id')
            outcome = request.data.get('outcome')
            
            if not all([match_id, bet_type_id, outcome]):
                return Response({
                    'error': 'Thiếu thông tin: match_id, bet_type_id, outcome'
                }, status=400)
            
            result = self.liability_service.calculate_net_liability(
                match_id, bet_type_id, outcome
            )
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': f'Lỗi tính toán liability: {str(e)}'
            }, status=500)

class VigorishMarginViewSet(viewsets.ViewSet):
    """ViewSet cho quản lý Vigorish/Margin"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.margin_service = VigorishMarginService()
    
    @action(detail=False, methods=['post'])
    def calculate_odds_with_margin(self, request):
        """Tính toán odds với margin"""
        try:
            true_probabilities = request.data.get('true_probabilities', {})
            target_margin = request.data.get('target_margin')
            
            if not true_probabilities:
                return Response({
                    'error': 'Thiếu thông tin: true_probabilities'
                }, status=400)
            
            result = self.margin_service.calculate_odds_with_margin(
                true_probabilities, target_margin
            )
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': f'Lỗi tính toán margin: {str(e)}'
            }, status=500)
    
    @action(detail=False, methods=['post'])
    def calculate_football_odds(self, request):
        """Tính toán odds cho trận đấu bóng đá"""
        try:
            home_team_strength = request.data.get('home_team_strength')
            away_team_strength = request.data.get('away_team_strength')
            draw_probability = request.data.get('draw_probability')
            target_margin = request.data.get('target_margin')
            
            if not all([home_team_strength, away_team_strength]):
                return Response({
                    'error': 'Thiếu thông tin: home_team_strength, away_team_strength'
                }, status=400)
            
            result = self.margin_service.calculate_football_match_odds(
                home_team_strength, away_team_strength, draw_probability, target_margin
            )
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': f'Lỗi tính toán football odds: {str(e)}'
            }, status=500)

class RiskThresholdViewSet(viewsets.ViewSet):
    """ViewSet cho quản lý ngưỡng rủi ro"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.threshold_service = RiskThresholdService()
    
    @action(detail=False, methods=['post'])
    def set_risk_thresholds(self, request):
        """Thiết lập ngưỡng rủi ro cho match"""
        try:
            match_id = request.data.get('match_id')
            bookmaker_type = request.data.get('bookmaker_type')
            main_threshold = request.data.get('main_threshold')
            promotion_threshold = request.data.get('promotion_threshold')
            
            if not all([match_id, bookmaker_type, main_threshold]):
                return Response({
                    'error': 'Thiếu thông tin: match_id, bookmaker_type, main_threshold'
                }, status=400)
            
            result = self.threshold_service.set_risk_thresholds(
                match_id, bookmaker_type, main_threshold, promotion_threshold
            )
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': f'Lỗi thiết lập threshold: {str(e)}'
            }, status=500)
    
    @action(detail=False, methods=['post'])
    def check_risk_threshold(self, request):
        """Kiểm tra ngưỡng rủi ro"""
        try:
            match_id = request.data.get('match_id')
            bet_type = request.data.get('bet_type')
            outcome = request.data.get('outcome')
            bet_amount = request.data.get('bet_amount')
            promotion_type = request.data.get('promotion_type')
            
            if not all([match_id, bet_type, outcome, bet_amount]):
                return Response({
                    'error': 'Thiếu thông tin: match_id, bet_type, outcome, bet_amount'
                }, status=400)
            
            result = self.threshold_service.check_risk_threshold(
                match_id, bet_type, outcome, bet_amount, promotion_type
            )
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': f'Lỗi kiểm tra threshold: {str(e)}'
            }, status=500)

class PromotionRiskViewSet(viewsets.ViewSet):
    """ViewSet cho quản lý rủi ro promotion"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.promotion_service = PromotionRiskService()
    
    @action(detail=False, methods=['post'])
    def calculate_promotion_risk(self, request):
        """Tính toán rủi ro cho promotion"""
        try:
            promotion_data = request.data.get('promotion_data', {})
            
            if not promotion_data:
                return Response({
                    'error': 'Thiếu thông tin: promotion_data'
                }, status=400)
            
            result = self.promotion_service.calculate_promotion_risk(promotion_data)
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': f'Lỗi tính toán promotion risk: {str(e)}'
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def get_promotion_risk_summary(self, request):
        """Lấy tổng quan rủi ro promotion cho match"""
        try:
            match_id = request.query_params.get('match_id')
            
            if not match_id:
                return Response({
                    'error': 'Thiếu thông tin: match_id'
                }, status=400)
            
            result = self.promotion_service.get_promotion_risk_summary(match_id)
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': f'Lỗi lấy promotion risk summary: {str(e)}'
            }, status=500)

class InPlayRiskViewSet(viewsets.ViewSet):
    """ViewSet cho quản lý rủi ro in-play"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.inplay_service = InPlayRiskService()
    
    @action(detail=False, methods=['post'])
    def recalculate_inplay_odds(self, request):
        """Tính toán lại odds cho in-play betting"""
        try:
            match_id = request.data.get('match_id')
            match_progress = request.data.get('match_progress', {})
            current_odds = request.data.get('current_odds', {})
            bookmaker_type = request.data.get('bookmaker_type', 'SYSTEM')
            
            if not match_id:
                return Response({
                    'error': 'Thiếu thông tin: match_id'
                }, status=400)
            
            result = self.inplay_service.recalculate_inplay_odds(
                match_id, match_progress, current_odds, bookmaker_type
            )
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': f'Lỗi tính toán in-play odds: {str(e)}'
            }, status=500)
    
    @action(detail=False, methods=['post'])
    def handle_match_event(self, request):
        """Xử lý sự kiện trong trận đấu"""
        try:
            match_id = request.data.get('match_id')
            event_type = request.data.get('event_type')
            event_data = request.data.get('event_data', {})
            
            if not all([match_id, event_type]):
                return Response({
                    'error': 'Thiếu thông tin: match_id, event_type'
                }, status=400)
            
            result = self.inplay_service.handle_match_event(
                match_id, event_type, event_data
            )
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': f'Lỗi xử lý match event: {str(e)}'
            }, status=500)

class BookmakerRoleViewSet(viewsets.ViewSet):
    """ViewSet cho quản lý vai trò nhà cái"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.role_service = BookmakerRoleManagementService()
    
    @action(detail=False, methods=['get'])
    def determine_bookmaker_role(self, request):
        """Xác định vai trò nhà cái cho user"""
        try:
            user_id = request.query_params.get('user_id')
            match_id = request.query_params.get('match_id')
            
            if not user_id:
                return Response({
                    'error': 'Thiếu thông tin: user_id'
                }, status=400)
            
            result = self.role_service.determine_bookmaker_role(user_id, match_id)
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': f'Lỗi xác định vai trò: {str(e)}'
            }, status=500)
    
    @action(detail=False, methods=['post'])
    def apply_risk_rules_by_role(self, request):
        """Áp dụng quy tắc rủi ro theo vai trò"""
        try:
            bookmaker_role = request.data.get('bookmaker_role', {})
            risk_data = request.data.get('risk_data', {})
            
            if not bookmaker_role:
                return Response({
                    'error': 'Thiếu thông tin: bookmaker_role'
                }, status=400)
            
            result = self.role_service.apply_risk_rules_by_role(bookmaker_role, risk_data)
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': f'Lỗi áp dụng risk rules: {str(e)}'
            }, status=500)

class RiskManagementOrchestratorViewSet(viewsets.ViewSet):
    """ViewSet cho Risk Management Orchestrator"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orchestrator = RiskManagementOrchestratorService()
    
    @action(detail=False, methods=['post'])
    def comprehensive_risk_assessment(self, request):
        """Đánh giá rủi ro toàn diện cho bet"""
        try:
            match_id = request.data.get('match_id')
            user_id = request.data.get('user_id')
            bet_data = request.data.get('bet_data', {})
            
            if not all([match_id, user_id]):
                return Response({
                    'error': 'Thiếu thông tin: match_id, user_id'
                }, status=400)
            
            result = self.orchestrator.comprehensive_risk_assessment(
                match_id, user_id, bet_data
            )
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': f'Lỗi đánh giá rủi ro: {str(e)}'
            }, status=500)
    
    @action(detail=False, methods=['post'])
    def setup_match_risk_management(self, request):
        """Thiết lập hệ thống quản lý rủi ro cho match"""
        try:
            match_id = request.data.get('match_id')
            bookmaker_type = request.data.get('bookmaker_type')
            main_threshold = request.data.get('main_threshold')
            promotion_threshold = request.data.get('promotion_threshold')
            
            if not all([match_id, bookmaker_type, main_threshold]):
                return Response({
                    'error': 'Thiếu thông tin: match_id, bookmaker_type, main_threshold'
                }, status=400)
            
            result = self.orchestrator.setup_match_risk_management(
                match_id, bookmaker_type, main_threshold, promotion_threshold
            )
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': f'Lỗi thiết lập risk management: {str(e)}'
            }, status=500)
    
    @action(detail=False, methods=['get'])
    def get_risk_dashboard_data(self, request):
        """Lấy dữ liệu cho dashboard quản lý rủi ro"""
        try:
            match_id = request.query_params.get('match_id')
            user_id = request.query_params.get('user_id')
            
            result = self.orchestrator.get_risk_dashboard_data(match_id, user_id)
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': f'Lỗi lấy dashboard data: {str(e)}'
            }, status=500)


# ============================================================================
# RISK-ADJUSTED OFFERED ODDS API VIEWS
# ============================================================================

class RiskAdjustedOddsAPIView(APIView):
    """API cho Risk-Adjusted Offered Odds Service"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = RiskAdjustedOddsService()
    
    def post(self, request):
        """Tính toán Risk-Adjusted Offered Odds"""
        try:
            # Validate input data
            required_fields = ['theoretical_odds', 'margin_factor', 'net_liability', 'risk_threshold']
            for field in required_fields:
                if field not in request.data:
                    return Response({
                        'error': f'Thiếu trường bắt buộc: {field}'
                    }, status=400)
            
            # Calculate risk-adjusted odds
            result = self.service.calculate_risk_adjusted_odds(
                theoretical_odds=Decimal(str(request.data['theoretical_odds'])),
                margin_factor=Decimal(str(request.data['margin_factor'])),
                net_liability=Decimal(str(request.data['net_liability'])),
                risk_threshold=Decimal(str(request.data['risk_threshold']))
            )
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': f'Lỗi tính toán risk-adjusted odds: {str(e)}'
            }, status=500)
    
    def get(self, request):
        """Lấy giải thích chi tiết về công thức"""
        try:
            # Validate input data
            required_fields = ['theoretical_odds', 'margin_factor', 'net_liability', 'risk_threshold']
            for field in required_fields:
                if field not in request.query_params:
                    return Response({
                        'error': f'Thiếu tham số bắt buộc: {field}'
                    }, status=400)
            
            # Get detailed explanation
            explanation = self.service.get_risk_adjustment_explanation(
                theoretical_odds=Decimal(str(request.query_params['theoretical_odds'])),
                margin_factor=Decimal(str(request.query_params['margin_factor'])),
                net_liability=Decimal(str(request.query_params['net_liability'])),
                risk_threshold=Decimal(str(request.query_params['risk_threshold']))
            )
            
            return Response(explanation)
            
        except Exception as e:
            return Response({
                'error': f'Lỗi tạo giải thích: {str(e)}'
            }, status=500)


class BatchRiskAdjustedOddsAPIView(APIView):
    """API cho tính toán batch Risk-Adjusted Offered Odds"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = RiskAdjustedOddsService()
    
    def post(self, request):
        """Tính toán batch Risk-Adjusted Offered Odds"""
        try:
            # Validate input data
            if 'odds_configs' not in request.data:
                return Response({
                    'error': 'Thiếu trường bắt buộc: odds_configs'
                }, status=400)
            
            odds_configs = request.data['odds_configs']
            if not isinstance(odds_configs, list) or len(odds_configs) == 0:
                return Response({
                    'error': 'odds_configs phải là một list không rỗng'
                }, status=400)
            
            # Calculate batch risk-adjusted odds
            result = self.service.calculate_batch_risk_adjusted_odds(odds_configs)
            
            return Response(result)
            
        except Exception as e:
            return Response({
                'error': f'Lỗi tính toán batch risk-adjusted odds: {str(e)}'
            }, status=500)


class RiskAdjustedOddsTestAPIView(APIView):
    """API để test các trường hợp khác nhau của Risk-Adjusted Offered Odds"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = RiskAdjustedOddsService()
    
    def get(self, request):
        """Chạy các test case mẫu"""
        try:
            test_cases = [
                {
                    'name': 'Tình huống AN TOÀN (L_ròng < 0)',
                    'theoretical_odds': '2.00',
                    'margin_factor': '1.05',
                    'net_liability': '-1000.00',
                    'risk_threshold': '10000.00'
                },
                {
                    'name': 'Tình huống RỦI RO THẤP',
                    'theoretical_odds': '2.50',
                    'margin_factor': '1.08',
                    'net_liability': '2000.00',
                    'risk_threshold': '10000.00'
                },
                {
                    'name': 'Tình huống RỦI RO TRUNG BÌNH',
                    'theoretical_odds': '3.00',
                    'margin_factor': '1.10',
                    'net_liability': '5000.00',
                    'risk_threshold': '10000.00'
                },
                {
                    'name': 'Tình huống RỦI RO CAO',
                    'theoretical_odds': '2.20',
                    'margin_factor': '1.12',
                    'net_liability': '8000.00',
                    'risk_threshold': '10000.00'
                },
                {
                    'name': 'Tình huống THỊ TRƯỜNG BỊ KHÓA',
                    'theoretical_odds': '1.50',
                    'margin_factor': '1.15',
                    'net_liability': '9500.00',
                    'risk_threshold': '10000.00'
                }
            ]
            
            results = {}
            for i, test_case in enumerate(test_cases):
                result = self.service.calculate_risk_adjusted_odds(
                    theoretical_odds=Decimal(test_case['theoretical_odds']),
                    margin_factor=Decimal(test_case['margin_factor']),
                    net_liability=Decimal(test_case['net_liability']),
                    risk_threshold=Decimal(test_case['risk_threshold'])
                )
                
                results[f"test_case_{i+1}"] = {
                    'name': test_case['name'],
                    'input': test_case,
                    'result': result
                }
            
            return Response({
                'success': True,
                'test_cases': results,
                'summary': {
                    'total_cases': len(test_cases),
                    'successful_cases': sum(1 for r in results.values() if r['result'].get('success', False)),
                    'locked_markets': sum(1 for r in results.values() if r['result'].get('market_locked', False))
                }
            })
            
        except Exception as e:
            return Response({
                'error': f'Lỗi chạy test cases: {str(e)}'
            }, status=500)