from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Count, Q

from .models import SagaTransaction, SagaEvent, SagaDefinition
from .serializers import (
    SagaTransactionSerializer, SagaEventSerializer,
    SagaDefinitionSerializer, SagaStartRequestSerializer, SagaStatusSerializer
)
from .orchestrator import SagaOrchestrator
import logging

logger = logging.getLogger(__name__)

class SagaTransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for saga transactions"""
    queryset = SagaTransaction.objects.all()
    serializer_class = SagaTransactionSerializer
    
    def get_queryset(self):
        queryset = SagaTransaction.objects.all()
        
        # Filter by user_id if provided
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by saga_type if provided
        saga_type = self.request.query_params.get('saga_type')
        if saga_type:
            queryset = queryset.filter(saga_type=saga_type)
        
        # Filter by status if provided
        saga_status = self.request.query_params.get('status')
        if saga_status:
            queryset = queryset.filter(status=saga_status)
        
        return queryset.order_by('-created_at')
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get detailed status of a saga"""
        saga = self.get_object()
        
        # Calculate progress
        total_steps = saga.steps.count()
        completed_steps = saga.steps.filter(status='completed').count()
        progress_percentage = (completed_steps / total_steps * 100) if total_steps > 0 else 0
        
        # Get current step
        current_step = saga.steps.filter(
            status__in=['pending', 'in_progress']
        ).order_by('step_order').first()
        
        status_data = {
            'saga_id': saga.id,
            'status': saga.status,
            'progress': {
                'total_steps': total_steps,
                'completed_steps': completed_steps,
                'percentage': round(progress_percentage, 2)
            },
            'current_step': current_step.step_name if current_step else None,
            'error_message': saga.error_message
        }
        
        serializer = SagaStatusSerializer(status_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def retry(self, request, pk=None):
        """Retry a failed saga"""
        saga = self.get_object()
        
        if saga.status not in ['failed', 'timeout']:
            return Response(
                {'detail': 'Only failed or timed out sagas can be retried'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if saga.retry_count >= saga.max_retries:
            return Response(
                {'detail': 'Maximum retry attempts exceeded'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Reset saga status
            saga.status = 'pending'
            saga.retry_count += 1
            saga.error_message = None
            saga.save()
            
            # Reset failed steps
            saga.steps.filter(status='failed').update(
                status='pending',
                error_message=None
            )
            
            # Start execution
            orchestrator = SagaOrchestrator()
            orchestrator.execute_saga(str(saga.id))
            
            return Response({'detail': 'Saga retry initiated'})
            
        except Exception as e:
            logger.error(f"Failed to retry saga {saga.id}: {e}")
            return Response(
                {'detail': f'Failed to retry saga: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['POST'])
def start_saga(request):
    """Start a new saga transaction"""
    serializer = SagaStartRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    try:
        orchestrator = SagaOrchestrator()
        saga_transaction = orchestrator.start_saga(
            saga_type=serializer.validated_data['saga_type'],
            user_id=serializer.validated_data['user_id'],
            input_data=serializer.validated_data['input_data'],
            correlation_id=serializer.validated_data.get('correlation_id')
        )
        
        response_serializer = SagaTransactionSerializer(saga_transaction)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Failed to start saga: {e}")
        return Response(
            {'detail': f'Failed to start saga: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
def saga_statistics(request):
    """Get saga statistics"""
    stats = SagaTransaction.objects.aggregate(
        total_sagas=Count('id'),
        pending_sagas=Count('id', filter=Q(status='pending')),
        in_progress_sagas=Count('id', filter=Q(status='in_progress')),
        completed_sagas=Count('id', filter=Q(status='completed')),
        failed_sagas=Count('id', filter=Q(status='failed')),
        compensated_sagas=Count('id', filter=Q(status='compensated')),
        timeout_sagas=Count('id', filter=Q(status='timeout'))
    )
    
    # Calculate success rate
    total = stats['total_sagas']
    completed = stats['completed_sagas']
    success_rate = (completed / total * 100) if total > 0 else 0
    
    stats['success_rate'] = round(success_rate, 2)
    stats['timestamp'] = timezone.now().isoformat()
    
    return Response(stats)

class SagaDefinitionViewSet(viewsets.ModelViewSet):
    """ViewSet for saga definitions"""
    queryset = SagaDefinition.objects.all()
    serializer_class = SagaDefinitionSerializer
    
    def get_queryset(self):
        queryset = SagaDefinition.objects.all()
        
        # Filter by saga_type if provided
        saga_type = self.request.query_params.get('saga_type')
        if saga_type:
            queryset = queryset.filter(saga_type=saga_type)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-created_at')

@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'healthy',
        'service': 'saga_orchestrator',
        'timestamp': timezone.now().isoformat()
    })

class SagaEventViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for saga events (read-only)"""
    queryset = SagaEvent.objects.all()
    serializer_class = SagaEventSerializer
    
    def get_queryset(self):
        queryset = SagaEvent.objects.all()
        
        # Filter by saga_transaction if provided
        saga_id = self.request.query_params.get('saga_id')
        if saga_id:
            queryset = queryset.filter(saga_transaction_id=saga_id)
        
        # Filter by event_type if provided
        event_type = self.request.query_params.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        return queryset.order_by('-created_at')


# ============================================================================
# CASH OUT SAGA API ENDPOINTS
# ============================================================================

@api_view(['POST'])
def start_cashout_saga(request):
    """Khởi tạo Cash Out Saga transaction"""
    try:
        bet_slip_id = request.data.get('bet_slip_id')
        user_id = request.data.get('user_id')
        bookmaker_type = request.data.get('bookmaker_type', 'SYSTEM')
        bookmaker_id = request.data.get('bookmaker_id', 'system')
        
        if not bet_slip_id or not user_id:
            return Response(
                {'detail': 'bet_slip_id và user_id là bắt buộc'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        orchestrator = SagaOrchestrator()
        saga_transaction = orchestrator.start_cashout_saga(
            bet_slip_id=bet_slip_id,
            user_id=user_id,
            bookmaker_type=bookmaker_type,
            bookmaker_id=bookmaker_id
        )
        
        response_data = {
            'message': 'Cash Out Saga đã được khởi tạo thành công',
            'saga_transaction_id': str(saga_transaction.id),
            'correlation_id': saga_transaction.correlation_id,
            'status': saga_transaction.status,
            'created_at': saga_transaction.created_at.isoformat()
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Failed to start cashout saga: {e}")
        return Response(
            {'detail': f'Không thể khởi tạo Cash Out Saga: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def rollback_cashout_saga(request):
    """Rollback Cash Out Saga transaction"""
    try:
        saga_transaction_id = request.data.get('saga_transaction_id')
        reason = request.data.get('reason', 'Rollback requested by user')
        
        if not saga_transaction_id:
            return Response(
                {'detail': 'saga_transaction_id là bắt buộc'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        orchestrator = SagaOrchestrator()
        success = orchestrator.rollback_cashout_saga(saga_transaction_id, reason)
        
        if success:
            response_data = {
                'message': 'Cash Out Saga đã được rollback thành công',
                'saga_transaction_id': saga_transaction_id,
                'status': 'rolled_back',
                'reason': reason,
                'timestamp': timezone.now().isoformat()
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'detail': 'Không thể rollback Cash Out Saga'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        logger.error(f"Failed to rollback cashout saga: {e}")
        return Response(
            {'detail': f'Không thể rollback Cash Out Saga: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_cashout_saga_status(request, saga_id):
    """Lấy trạng thái chi tiết của Cash Out Saga"""
    try:
        saga_transaction = SagaTransaction.objects.get(id=saga_id, saga_type='cashout_flow')
        
        # Lấy thông tin các bước
        steps_info = []
        for step in saga_transaction.steps.order_by('step_order'):
            step_data = {
                'step_name': step.step_name,
                'step_order': step.step_order,
                'status': step.status,
                'started_at': step.started_at.isoformat() if step.started_at else None,
                'completed_at': step.completed_at.isoformat() if step.completed_at else None,
                'error_message': step.error_message
            }
            steps_info.append(step_data)
        
        # Lấy các events
        events_info = []
        for event in saga_transaction.events.order_by('-created_at')[:10]:  # 10 events gần nhất
            event_data = {
                'event_type': event.event_type,
                'message': event.message,
                'created_at': event.created_at.isoformat()
            }
            events_info.append(event_data)
        
        response_data = {
            'saga_id': str(saga_transaction.id),
            'correlation_id': saga_transaction.correlation_id,
            'status': saga_transaction.status,
            'user_id': saga_transaction.user_id,
            'input_data': saga_transaction.input_data,
            'context_data': saga_transaction.context_data,
            'created_at': saga_transaction.created_at.isoformat(),
            'started_at': saga_transaction.started_at.isoformat() if saga_transaction.started_at else None,
            'completed_at': saga_transaction.completed_at.isoformat() if saga_transaction.completed_at else None,
            'steps': steps_info,
            'recent_events': events_info,
            'progress': {
                'total_steps': len(steps_info),
                'completed_steps': len([s for s in steps_info if s['status'] == 'completed']),
                'failed_steps': len([s for s in steps_info if s['status'] == 'failed']),
                'percentage': round((len([s for s in steps_info if s['status'] == 'completed']) / len(steps_info) * 100) if steps_info else 0, 2)
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except SagaTransaction.DoesNotExist:
        return Response(
            {'detail': 'Không tìm thấy Cash Out Saga'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Failed to get cashout saga status: {e}")
        return Response(
            {'detail': f'Không thể lấy trạng thái Cash Out Saga: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def list_cashout_sagas(request):
    """Lấy danh sách các Cash Out Saga"""
    try:
        # Filter theo user_id nếu có
        user_id = request.query_params.get('user_id')
        status_filter = request.query_params.get('status')
        
        queryset = SagaTransaction.objects.filter(saga_type='cashout_flow')
        
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Sắp xếp theo thời gian tạo mới nhất
        sagas = queryset.order_by('-created_at')
        
        # Pagination đơn giản
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        
        paginated_sagas = sagas[start:end]
        
        saga_list = []
        for saga in paginated_sagas:
            saga_data = {
                'saga_id': str(saga.id),
                'correlation_id': saga.correlation_id,
                'user_id': saga.user_id,
                'status': saga.status,
                'bet_slip_id': saga.input_data.get('bet_slip_id'),
                'bookmaker_type': saga.input_data.get('bookmaker_type'),
                'created_at': saga.created_at.isoformat(),
                'completed_at': saga.completed_at.isoformat() if saga.completed_at else None,
                'error_message': saga.error_message
            }
            saga_list.append(saga_data)
        
        response_data = {
            'sagas': saga_list,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': sagas.count(),
                'total_pages': (sagas.count() + page_size - 1) // page_size
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Failed to list cashout sagas: {e}")
        return Response(
            {'detail': f'Không thể lấy danh sách Cash Out Saga: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def retry_cashout_saga_step(request, saga_id, step_name):
    """Retry một bước cụ thể trong Cash Out Saga"""
    try:
        saga_transaction = SagaTransaction.objects.get(id=saga_id, saga_type='cashout_flow')
        step = saga_transaction.steps.filter(step_name=step_name).first()
        
        if not step:
            return Response(
                {'detail': f'Không tìm thấy step {step_name}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if step.status not in ['failed', 'timeout']:
            return Response(
                {'detail': f'Chỉ có thể retry các step đã thất bại hoặc timeout'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset step status
        step.status = 'pending'
        step.error_message = None
        step.retry_count += 1
        step.save()
        
        # Log retry event
        SagaEvent.objects.create(
            saga_transaction=saga_transaction,
            saga_step=step,
            event_type='step_retry_attempted',
            message=f"Retry attempt {step.retry_count} for step {step_name}"
        )
        
        # Re-execute the step
        orchestrator = SagaOrchestrator()
        success = orchestrator._execute_step(step)
        
        if success:
            response_data = {
                'message': f'Step {step_name} đã được retry thành công',
                'saga_id': str(saga_id),
                'step_name': step_name,
                'status': step.status
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {'detail': f'Retry step {step_name} thất bại'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except SagaTransaction.DoesNotExist:
        return Response(
            {'detail': 'Không tìm thấy Cash Out Saga'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Failed to retry cashout saga step: {e}")
        return Response(
            {'detail': f'Không thể retry step: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

