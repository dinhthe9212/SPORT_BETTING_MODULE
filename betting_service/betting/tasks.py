from celery import shared_task
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, name='betting.monitor_auto_orders')
def monitor_auto_orders_task(self):
    """
    Task Celery để giám sát lệnh tự động (Chốt Lời & Cắt Lỗ)
    Chạy định kỳ mỗi 10 giây
    """
    try:
        from .services import AutoCashoutMonitorService
        
        logger.info("Bắt đầu task giám sát lệnh tự động")
        
        # Khởi tạo service
        monitor_service = AutoCashoutMonitorService()
        
        # Bắt đầu giám sát
        result = monitor_service.start_monitoring()
        
        if result['success']:
            logger.info(f"Task giám sát hoàn thành: {result.get('processed', 0)} phiếu cược đã được xử lý")
            return {
                'status': 'success',
                'processed_count': result.get('processed', 0),
                'triggered_count': result.get('triggered', 0),
                'timestamp': timezone.now().isoformat()
            }
        else:
            logger.error(f"Task giám sát thất bại: {result.get('error', 'Unknown error')}")
            return {
                'status': 'error',
                'error': result.get('error', 'Unknown error'),
                'timestamp': timezone.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Lỗi trong task giám sát lệnh tự động: {e}")
        # Retry task sau 30 giây nếu có lỗi
        raise self.retry(countdown=30, max_retries=3)


@shared_task(bind=True, name='betting.suspend_auto_orders_for_match')
def suspend_auto_orders_for_match_task(self, match_id, reason="Market suspended"):
    """
    Task để tạm dừng tất cả lệnh tự động cho một trận đấu
    """
    try:
        from .services import AutoCashoutMonitorService
        
        logger.info(f"Bắt đầu task tạm dừng lệnh tự động cho match {match_id}")
        
        # Khởi tạo service
        monitor_service = AutoCashoutMonitorService()
        
        # Tạm dừng lệnh tự động
        result = monitor_service.suspend_auto_orders_for_market(match_id, reason)
        
        if result['success']:
            logger.info(f"Đã tạm dừng {result.get('suspended_count', 0)} lệnh tự động cho match {match_id}")
            return {
                'status': 'success',
                'suspended_count': result.get('suspended_count', 0),
                'match_id': match_id,
                'timestamp': timezone.now().isoformat()
            }
        else:
            logger.error(f"Lỗi tạm dừng lệnh tự động cho match {match_id}: {result.get('error', 'Unknown error')}")
            return {
                'status': 'error',
                'error': result.get('error', 'Unknown error'),
                'match_id': match_id,
                'timestamp': timezone.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Lỗi trong task tạm dừng lệnh tự động: {e}")
        raise self.retry(countdown=30, max_retries=3)


@shared_task(bind=True, name='betting.resume_auto_orders_for_match')
def resume_auto_orders_for_match_task(self, match_id):
    """
    Task để khôi phục tất cả lệnh tự động cho một trận đấu
    """
    try:
        from .services import AutoCashoutMonitorService
        
        logger.info(f"Bắt đầu task khôi phục lệnh tự động cho match {match_id}")
        
        # Khởi tạo service
        monitor_service = AutoCashoutMonitorService()
        
        # Khôi phục lệnh tự động
        result = monitor_service.resume_auto_orders_for_market(match_id)
        
        if result['success']:
            logger.info(f"Đã khôi phục {result.get('resumed_count', 0)} lệnh tự động cho match {match_id}")
            return {
                'status': 'success',
                'resumed_count': result.get('resumed_count', 0),
                'match_id': match_id,
                'timestamp': timezone.now().isoformat()
            }
        else:
            logger.error(f"Lỗi khôi phục lệnh tự động cho match {match_id}: {result.get('error', 'Unknown error')}")
            return {
                'status': 'error',
                'error': result.get('error', 'Unknown error'),
                'match_id': match_id,
                'timestamp': timezone.now().isoformat()
            }
            
    except Exception as e:
        logger.error(f"Lỗi trong task khôi phục lệnh tự động: {e}")
        raise self.retry(countdown=30, max_retries=3)


@shared_task(bind=True, name='betting.cleanup_completed_auto_orders')
def cleanup_completed_auto_orders_task(self):
    """
    Task để dọn dẹp các lệnh tự động đã hoàn thành
    Chạy mỗi ngày lúc 2:00 AM
    """
    try:
        from .models import BetSlip
        from django.utils import timezone
        from datetime import timedelta
        
        logger.info("Bắt đầu task dọn dẹp lệnh tự động đã hoàn thành")
        
        # Xóa các lệnh tự động đã hoàn thành hơn 30 ngày trước
        cutoff_date = timezone.now() - timedelta(days=30)
        
        deleted_count = BetSlip.objects.filter(
            auto_order_status='COMPLETED',
            auto_order_triggered_at__lt=cutoff_date
        ).update(
            take_profit_threshold=None,
            stop_loss_threshold=None,
            auto_order_reason=None
        )
        
        logger.info(f"Đã dọn dẹp {deleted_count} lệnh tự động đã hoàn thành")
        
        return {
            'status': 'success',
            'deleted_count': deleted_count,
            'timestamp': timezone.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Lỗi trong task dọn dẹp lệnh tự động: {e}")
        raise self.retry(countdown=300, max_retries=3)  # Retry sau 5 phút
