from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import (
    IndividualBookmaker, RiskAlert, TutorialProgress,
    BookmakerPerformance
)


@receiver(post_save, sender=IndividualBookmaker)
def create_welcome_alert(sender, instance, created, **kwargs):
    """Tạo welcome alert khi bookmaker mới được tạo"""
    if created:
        RiskAlert.objects.create(
            user_id=instance.user_id,
            alert_type='WELCOME',
            severity='LOW',
            title='Chào mừng đến với Individual Bookmaker Service',
            message='Chúng tôi sẽ giúp bạn quản lý rủi ro và cải thiện hiệu suất cá cược. Hãy bắt đầu với các tutorials cơ bản.',
            is_read=False
        )


@receiver(post_save, sender=IndividualBookmaker)
def check_risk_level_change(sender, instance, **kwargs):
    """Kiểm tra thay đổi risk level và tạo alert nếu cần"""
    if not kwargs.get('created'):
        try:
            old_instance = IndividualBookmaker.objects.get(id=instance.id)
            if old_instance.risk_level != instance.risk_level:
                # Tạo alert cho thay đổi risk level
                severity_map = {
                    'LOW': 'LOW',
                    'MEDIUM': 'MEDIUM',
                    'HIGH': 'HIGH',
                    'CRITICAL': 'CRITICAL'
                }
                
                RiskAlert.objects.create(
                    user_id=instance.user_id,
                    alert_type='RISK_LEVEL_CHANGE',
                    severity=severity_map.get(instance.risk_level, 'MEDIUM'),
                    title=f'Thay đổi mức độ rủi ro: {instance.risk_level}',
                    message=f'Mức độ rủi ro của bạn đã thay đổi từ {old_instance.risk_level} thành {instance.risk_level}. Vui lòng kiểm tra và thực hiện các biện pháp giảm thiểu rủi ro.',
                    is_read=False
                )
        except IndividualBookmaker.DoesNotExist:
            pass


@receiver(post_save, sender=TutorialProgress)
def update_performance_on_tutorial_completion(sender, instance, **kwargs):
    """Cập nhật performance khi tutorial hoàn thành"""
    if instance.is_completed and not kwargs.get('created'):
        try:
            # Cập nhật performance score
            bookmaker = IndividualBookmaker.objects.filter(
                user_id=instance.user_id
            ).first()
            
            if bookmaker:
                # Tăng performance score dựa trên tutorial completion
                performance_bonus = 2.0  # 2 điểm cho mỗi tutorial hoàn thành
                bookmaker.performance_score = min(
                    bookmaker.performance_score + performance_bonus, 100
                )
                bookmaker.save()
                
                # Tạo performance record
                BookmakerPerformance.objects.create(
                    user_id=instance.user_id,
                    period='TUTORIAL_COMPLETION',
                    performance_type='EDUCATION',
                    performance_score=bookmaker.performance_score,
                    metrics_data={
                        'tutorial_id': instance.tutorial.id,
                        'tutorial_title': instance.tutorial.title,
                        'completion_bonus': performance_bonus
                    },
                    notes=f'Tutorial "{instance.tutorial.title}" completed'
                )
                
        except Exception as e:
            # Log error nhưng không làm crash app
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating performance on tutorial completion: {str(e)}")


@receiver(post_save, sender=RiskAlert)
def log_alert_creation(sender, instance, created, **kwargs):
    """Log việc tạo alert mới"""
    if created:
        import logging
        logger = logging.getLogger(__name__)
        logger.info(
            f"Risk alert created: {instance.alert_type} - {instance.severity} "
            f"for user {instance.user_id}: {instance.title}"
        )


@receiver(post_delete, sender=IndividualBookmaker)
def cleanup_user_data(sender, instance, **kwargs):
    """Dọn dẹp dữ liệu khi bookmaker bị xóa"""
    try:
        # Xóa tất cả alerts
        RiskAlert.objects.filter(user_id=instance.user_id).delete()
        
        # Xóa tất cả tutorial progress
        TutorialProgress.objects.filter(user_id=instance.user_id).delete()
        
        # Xóa tất cả performance records
        BookmakerPerformance.objects.filter(user_id=instance.user_id).delete()
        
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Cleaned up data for deleted bookmaker user {instance.user_id}")
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error cleaning up user data: {str(e)}")


# Signal để tạo performance record định kỳ
@receiver(post_save, sender=IndividualBookmaker)
def schedule_performance_update(sender, instance, **kwargs):
    """Lên lịch cập nhật performance định kỳ"""
    try:
        # Kiểm tra xem có cần tạo performance record mới không
        last_performance = BookmakerPerformance.objects.filter(
            user_id=instance.user_id,
            period='MONTHLY'
        ).order_by('-created_at').first()
        
        if not last_performance or \
           (timezone.now() - last_performance.created_at).days >= 30:
            
            # Tạo performance record mới
            BookmakerPerformance.objects.create(
                user_id=instance.user_id,
                period='MONTHLY',
                performance_type='OVERALL',
                performance_score=instance.performance_score,
                metrics_data={
                    'total_bets': instance.total_bets,
                    'win_rate': instance.win_rate,
                    'total_profit': instance.total_profit,
                    'risk_level': instance.risk_level,
                    'risk_score': instance.risk_score
                },
                notes='Monthly performance update'
            )
            
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error scheduling performance update: {str(e)}")
