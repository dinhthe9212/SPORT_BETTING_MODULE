from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
import logging
from django.utils import timezone

from .models import (
    IndividualBookmaker, RiskEducationTutorial, RiskAlert, BestPractice, BookmakerPerformance
)
from .serializers import (
    IndividualBookmakerSerializer, RiskEducationTutorialSerializer,
    RiskAlertSerializer, BestPracticeSerializer,
    BookmakerPerformanceSerializer
)
from .services import (
    BookmakerDashboardService, RiskEducationService,
    RiskAlertService, PerformanceAnalyticsService
)

logger = logging.getLogger(__name__)


class DashboardView(APIView):
    """Dashboard chính cho Individual Bookmaker"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user_id = request.user.id
            dashboard_service = BookmakerDashboardService()
            dashboard_data = dashboard_service.get_dashboard_data(user_id)
            
            return Response({
                'status': 'success',
                'data': dashboard_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Không thể tải dữ liệu dashboard'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RiskOverviewView(APIView):
    """Tổng quan về rủi ro"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user_id = request.user.id
            risk_service = RiskAlertService()
            risk_data = risk_service.get_risk_overview(user_id)
            
            return Response({
                'status': 'success',
                'data': risk_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting risk overview: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Không thể tải dữ liệu rủi ro'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EducationView(APIView):
    """Hệ thống giáo dục rủi ro"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user_id = request.user.id
            education_service = RiskEducationService()
            tutorials = education_service.get_user_tutorials(user_id)
            
            return Response({
                'status': 'success',
                'data': tutorials
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting education data: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Không thể tải dữ liệu giáo dục'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Đánh dấu hoàn thành tutorial"""
        try:
            tutorial_id = request.data.get('tutorial_id')
            user_id = request.user.id
            
            education_service = RiskEducationService()
            result = education_service.mark_tutorial_completed(user_id, tutorial_id)
            
            return Response({
                'status': 'success',
                'data': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error marking tutorial completed: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Không thể cập nhật tiến độ'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AlertsView(APIView):
    """Quản lý cảnh báo rủi ro"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user_id = request.user.id
            alert_service = RiskAlertService()
            alerts = alert_service.get_user_alerts(user_id)
            
            return Response({
                'status': 'success',
                'data': alerts
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting alerts: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Không thể tải danh sách cảnh báo'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Đánh dấu cảnh báo đã đọc"""
        try:
            alert_id = request.data.get('alert_id')
            user_id = request.user.id
            
            alert_service = RiskAlertService()
            result = alert_service.mark_alert_read(user_id, alert_id)
            
            return Response({
                'status': 'success',
                'data': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error marking alert read: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Không thể cập nhật trạng thái cảnh báo'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PerformanceView(APIView):
    """Phân tích hiệu suất"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user_id = request.user.id
            performance_service = PerformanceAnalyticsService()
            performance_data = performance_service.get_user_performance(user_id)
            
            return Response({
                'status': 'success',
                'data': performance_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting performance data: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Không thể tải dữ liệu hiệu suất'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BestPracticesView(APIView):
    """Quản lý best practices"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            practices = BestPractice.objects.filter(is_active=True).order_by('-created_at')
            serializer = BestPracticeSerializer(practices, many=True)
            
            return Response({
                'status': 'success',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting best practices: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'Không thể tải best practices'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ViewSets cho quản lý CRUD
class IndividualBookmakerViewSet(ModelViewSet):
    """ViewSet cho quản lý Individual Bookmaker"""
    queryset = IndividualBookmaker.objects.all()
    serializer_class = IndividualBookmakerSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_id', 'status', 'risk_level']
    search_fields = ['user__username', 'user__email']
    ordering_fields = ['created_at', 'risk_level', 'performance_score']
    ordering = ['-created_at']


class RiskEducationTutorialViewSet(ModelViewSet):
    """ViewSet cho quản lý Tutorials"""
    queryset = RiskEducationTutorial.objects.all()
    serializer_class = RiskEducationTutorialSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category', 'difficulty_level', 'is_active']
    search_fields = ['title', 'description', 'content']
    ordering_fields = ['created_at', 'difficulty_level', 'duration_minutes']
    ordering = ['created_at']


class RiskAlertViewSet(ModelViewSet):
    """ViewSet cho quản lý Risk Alerts"""
    queryset = RiskAlert.objects.all()
    serializer_class = RiskAlertSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_id', 'alert_type', 'severity', 'is_read']
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'severity', 'is_read']
    ordering = ['-created_at']


class BookmakerPerformanceViewSet(ModelViewSet):
    """ViewSet cho quản lý Performance"""
    queryset = BookmakerPerformance.objects.all()
    serializer_class = BookmakerPerformanceSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['user_id', 'period', 'performance_type']
    search_fields = ['notes']
    ordering_fields = ['created_at', 'period', 'performance_score']
    ordering = ['-created_at']


# API endpoints cho webhook và tích hợp
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def webhook_risk_update(request):
    """Webhook nhận cập nhật rủi ro từ Risk Management Service"""
    try:
        data = request.data
        user_id = data.get('user_id')
        risk_level = data.get('risk_level')
        risk_score = data.get('risk_score')
        
        # Cập nhật thông tin rủi ro
        bookmaker, created = IndividualBookmaker.objects.get_or_create(
            user_id=user_id,
            defaults={'risk_level': risk_level, 'risk_score': risk_score}
        )
        
        if not created:
            bookmaker.risk_level = risk_level
            bookmaker.risk_score = risk_score
            bookmaker.save()
        
        # Tạo cảnh báo nếu cần
        if risk_level in ['HIGH', 'CRITICAL']:
            RiskAlert.objects.create(
                user_id=user_id,
                alert_type='RISK_LEVEL_CHANGE',
                severity='HIGH' if risk_level == 'HIGH' else 'CRITICAL',
                title=f'Thay đổi mức độ rủi ro: {risk_level}',
                message=f'Mức độ rủi ro của bạn đã thay đổi thành {risk_level}. Vui lòng kiểm tra và thực hiện các biện pháp giảm thiểu rủi ro.',
                is_read=False
            )
        
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error processing risk update webhook: {str(e)}")
        return Response({
            'status': 'error',
            'message': 'Không thể xử lý webhook'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def health_check(request):
    """Health check endpoint"""
    try:
        # Kiểm tra kết nối database
        IndividualBookmaker.objects.count()
        
        return Response({
            'status': 'healthy',
            'service': 'Individual Bookmaker Service',
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return Response({
            'status': 'unhealthy',
            'service': 'Individual Bookmaker Service',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
