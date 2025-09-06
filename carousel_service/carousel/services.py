from django.utils import timezone
from django.core.cache import cache
import random
import sys
import os
from .models import FeaturedEvent, UserProductPurchase

# Import cache utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))
try:
    from cache_settings import get_cache_key, get_cache_timeout
except ImportError:
    # Fallback if cache_settings not available
    def get_cache_key(category, key_type, **kwargs):
        return f"{category}:{key_type}:{':'.join(str(v) for v in kwargs.values())}"
    def get_cache_timeout(category, key_type):
        return 300


class CarouselService:
    """Service để xử lý logic carousel với prioritization"""
    
    @staticmethod
    def get_user_purchase_status(user, featured_event):
        """Kiểm tra trạng thái mua của user cho một sản phẩm"""
        if not user or user.is_anonymous:
            return 'CHUA_MUA'
        
        try:
            purchase = UserProductPurchase.objects.get(
                user=user, 
                featured_event=featured_event,
                status__in=['CONFIRMED', 'SETTLED']
            )
            return 'DA_MUA'
        except UserProductPurchase.DoesNotExist:
            return 'CHUA_MUA'
    
    @staticmethod
    def get_prioritized_carousel_items(user=None, limit=20, device_type='desktop'):
        """
        Lấy danh sách carousel items đã được ưu tiên theo quy tắc business:
        1. Sản phẩm chưa_mua luôn được ưu tiên lên đầu
        2. Trong cùng nhóm trạng thái, sắp xếp ngẫu nhiên
        3. Điều chỉnh số lượng theo thiết bị
        """
        
        # Điều chỉnh limit theo thiết bị
        device_limits = {
            'desktop': limit,
            'tablet': limit, 
            'mobile': min(limit, 15)  # Mobile giới hạn 15 items
        }
        actual_limit = device_limits.get(device_type, limit)
        
        # Lấy tất cả items active
        all_items = FeaturedEvent.objects.filter(is_active=True)
        
        if not user or user.is_anonymous:
            # User chưa đăng nhập - tất cả đều là chưa_mua
            items_list = list(all_items)
            random.shuffle(items_list)
            return items_list[:actual_limit]
        
        # Lấy danh sách sản phẩm đã mua của user
        purchased_ids = UserProductPurchase.objects.filter(
            user=user,
            status__in=['CONFIRMED', 'SETTLED']
        ).values_list('featured_event_id', flat=True)
        
        # Phân chia thành 2 nhóm
        chua_mua_items = list(all_items.exclude(id__in=purchased_ids))
        da_mua_items = list(all_items.filter(id__in=purchased_ids))
        
        # Xáo trộn ngẫu nhiên trong từng nhóm
        random.shuffle(chua_mua_items)
        random.shuffle(da_mua_items)
        
        # Kết hợp: chưa_mua trước, đã_mua sau
        prioritized_items = chua_mua_items + da_mua_items
        
        return prioritized_items[:actual_limit]
    
    @staticmethod
    def get_randomized_items(user=None, limit=20, device_type='desktop', exclude_recent=True):
        """
        Tạo chuỗi sản phẩm ngẫu nhiên mới cho auto-refresh
        """
        # Nếu exclude_recent, loại bỏ items vừa hiển thị gần đây
        recent_threshold = timezone.now() - timezone.timedelta(minutes=30)
        
        queryset = FeaturedEvent.objects.filter(is_active=True)
        
        if exclude_recent:
            # Logic để exclude items đã hiển thị gần đây có thể được thêm vào đây
            pass
        
        return CarouselService.get_prioritized_carousel_items(
            user=user, 
            limit=limit, 
            device_type=device_type
        )
    
    @staticmethod
    def get_display_count_by_device(device_type='desktop'):
        """Trả về số lượng sản phẩm hiển thị theo thiết bị"""
        display_counts = {
            'desktop': 4.5,    # 4.5 sản phẩm
            'tablet': 4.5,     # 4.5 sản phẩm  
            'mobile': 2.5,     # 2.5 sản phẩm (luôn để lộ một phần để khuyến khích vuốt)
        }
        return display_counts.get(device_type, 4.5)
    
    @staticmethod
    def record_user_purchase(user, featured_event, stake_amount, odds_at_purchase):
        """Ghi nhận việc mua sản phẩm của user"""
        purchase, created = UserProductPurchase.objects.get_or_create(
            user=user,
            featured_event=featured_event,
            defaults={
                'stake_amount': stake_amount,
                'odds_at_purchase': odds_at_purchase,
                'status': 'PENDING'
            }
        )
        
        if not created:
            # Cập nhật nếu đã tồn tại
            purchase.stake_amount = stake_amount
            purchase.odds_at_purchase = odds_at_purchase
            purchase.status = 'PENDING'
            purchase.save()
        
        return purchase
    
    @staticmethod
    def confirm_purchase(purchase_id):
        """Xác nhận đơn hàng - trigger real-time update"""
        try:
            purchase = UserProductPurchase.objects.get(id=purchase_id)
            purchase.status = 'CONFIRMED'
            purchase.save()
            
            # Cập nhật thống kê sản phẩm
            featured_event = purchase.featured_event
            featured_event.total_purchases += 1
            featured_event.save()
            
            # Trigger real-time update (có thể dùng WebSocket hoặc Server-Sent Events)
            CarouselService._trigger_realtime_update(purchase.user, featured_event)
            
            return purchase
        except UserProductPurchase.DoesNotExist:
            return None
    
    @staticmethod
    def _trigger_realtime_update(user, featured_event):
        """Trigger real-time update cho frontend (placeholder for WebSocket implementation)"""
        # TODO: Implement WebSocket hoặc Server-Sent Events
        # Để gửi thông báo real-time cho frontend về việc thay đổi trạng thái
        pass
    
    @staticmethod
    def get_carousel_items_with_status(user=None, limit=20, device_type='desktop'):
        """
        Lấy carousel items kèm theo trạng thái mua cho user - WITH CACHING
        """
        user_id = user.id if user and user.is_authenticated else 'anonymous'
        
        # Try cache first
        cache_key = get_cache_key('carousel', 'prioritized', 
                                user_id=user_id, device_type=device_type, limit=limit)
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return cached_data
        
        # Generate fresh data
        items = CarouselService.get_prioritized_carousel_items(user, limit, device_type)
        
        result = []
        for item in items:
            item_data = {
                'id': item.id,
                'event_id': item.event_id,
                'title': item.title,
                'description': item.description,
                'image_url': item.image_url,
                'current_odds': float(item.current_odds),
                'stake_type': item.stake_type,
                'fixed_stake_value': float(item.fixed_stake_value) if item.fixed_stake_value else None,
                'min_stake': float(item.min_stake),
                'max_stake': float(item.max_stake),
                'purchase_status': item.get_purchase_status_for_user(user),
                'total_purchases': item.total_purchases,
                'created_at': item.created_at.isoformat(),
                'updated_at': item.updated_at.isoformat(),
            }
            result.append(item_data)
        
        # Cache the result
        user_id = user.id if user and user.is_authenticated else 'anonymous'
        cache_key = get_cache_key('carousel', 'prioritized', 
                                user_id=user_id, device_type=device_type, limit=limit)
        timeout = get_cache_timeout('carousel', 'prioritized_items')
        cache.set(cache_key, result, timeout)
        
        return result


class CarouselAutoRefreshService:
    """Service để xử lý auto-refresh carousel"""
    
    @staticmethod
    def should_refresh(last_refresh_time, current_position, total_items):
        """Kiểm tra xem có nên refresh không"""
        # Refresh khi đã xem hết tất cả items
        if current_position >= total_items - 1:
            return True
        
        # Hoặc refresh sau một khoảng thời gian nhất định
        time_threshold = timezone.now() - timezone.timedelta(minutes=10)
        if last_refresh_time and last_refresh_time < time_threshold:
            return True
        
        return False
    
    @staticmethod
    def get_refresh_interval():
        """Trả về interval cho auto-refresh (giây)"""
        return 5  # 5 giây pause trước khi refresh
