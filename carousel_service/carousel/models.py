from django.db import models
from django.conf import settings
from decimal import Decimal

class FeaturedEvent(models.Model):
    """Model cho sản phẩm cược trong carousel"""
    
    PURCHASE_STATUS_CHOICES = [
        ('CHUA_MUA', 'Chưa mua'),
        ('DA_MUA', 'Đã mua'),
    ]
    
    # Assuming event_id links to a Match in betting_service
    event_id = models.CharField(max_length=255, unique=True) # ID of the event from betting_service
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    image_url = models.URLField(blank=True, null=True)
    order = models.IntegerField(default=0) # Order in which it appears in the carousel
    is_active = models.BooleanField(default=True)
    
    # Thông tin sản phẩm cược
    fixed_stake_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          help_text='Giá trị cược cố định (nếu có)')
    stake_type = models.CharField(max_length=20, choices=[
        ('FIXED', 'Cược cố định'),
        ('FREE', 'Cược tự do')
    ], default='FREE')
    
    # Thông tin odds
    current_odds = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('1.00'))
    min_stake = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10.00'))
    max_stake = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('10000.00'))
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Thống kê
    total_purchases = models.IntegerField(default=0, help_text='Tổng số lượt mua')
    popularity_score = models.IntegerField(default=0, help_text='Điểm phổ biến để sắp xếp')

    class Meta:
        ordering = ["order", "-created_at"]
        indexes = [
            models.Index(fields=['is_active', 'order']),
            models.Index(fields=['popularity_score']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.title
    
    def get_purchase_status_for_user(self, user):
        """Lấy trạng thái mua của user cho sản phẩm này"""
        if user.is_anonymous:
            return 'CHUA_MUA'
            
        # Kiểm tra xem user đã mua sản phẩm này chưa
        from .services import CarouselService
        return CarouselService.get_user_purchase_status(user, self)
    
    @classmethod
    def get_prioritized_items(cls, user=None, limit=20):
        """Lấy danh sách items đã được ưu tiên theo quy tắc business"""
        from .services import CarouselService
        return CarouselService.get_prioritized_carousel_items(user, limit)


class UserProductPurchase(models.Model):
    """Model để track việc mua sản phẩm của user"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                           related_name='product_purchases')
    featured_event = models.ForeignKey(FeaturedEvent, on_delete=models.CASCADE,
                                     related_name='user_purchases')
    purchased_at = models.DateTimeField(auto_now_add=True)
    stake_amount = models.DecimalField(max_digits=10, decimal_places=2)
    odds_at_purchase = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Trạng thái đơn hàng
    STATUS_CHOICES = [
        ('PENDING', 'Chờ xử lý'),
        ('CONFIRMED', 'Đã xác nhận'),
        ('SETTLED', 'Đã thanh toán'),
        ('CANCELLED', 'Đã hủy'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    class Meta:
        unique_together = ('user', 'featured_event')
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['featured_event', 'status']),
            models.Index(fields=['purchased_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.featured_event.title}"
