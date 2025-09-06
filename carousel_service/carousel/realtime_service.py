"""
Real-time Notification Service for Carousel
Gửi WebSocket messages cho frontend updates
Cost: $0 (Django Channels built-in)
"""

import logging
from typing import Dict, Any, List, Optional
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone

logger = logging.getLogger('carousel')


class CarouselRealtimeService:
    """Service để gửi real-time notifications via WebSocket"""
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
    
    def notify_item_updated(self, item_id: str, changes: Dict[str, Any], 
                          updated_fields: List[str] = None):
        """
        Thông báo khi carousel item được update
        
        Args:
            item_id: ID của item
            changes: Dict các thay đổi (field: new_value)
            updated_fields: List các fields đã thay đổi
        """
        try:
            if not self.channel_layer:
                logger.warning("Channel layer not configured for real-time notifications")
                return
            
            # Send to item-specific group
            item_group = f"carousel_item_{item_id}"
            
            message = {
                'type': 'carousel_item_updated',
                'item_id': str(item_id),
                'changes': changes,
                'updated_fields': updated_fields or [],
                'timestamp': timezone.now().isoformat()
            }
            
            async_to_sync(self.channel_layer.group_send)(item_group, message)
            
            logger.info(f"Sent item update notification: item_id={item_id}, changes={changes}")
            
        except Exception as e:
            logger.error(f"Error sending item update notification: {e}")
    
    def notify_purchase_confirmed(self, user_id: int, item_id: str, purchase_id: str):
        """
        Thông báo khi purchase được confirm
        
        Args:
            user_id: ID của user
            item_id: ID của item
            purchase_id: ID của purchase
        """
        try:
            if not self.channel_layer:
                return
            
            # Send to user's personal channel
            user_group = f"carousel_carousel_user_{user_id}"
            
            message = {
                'type': 'carousel_purchase_confirmed',
                'item_id': str(item_id),
                'purchase_id': str(purchase_id),
                'timestamp': timezone.now().isoformat()
            }
            
            async_to_sync(self.channel_layer.group_send)(user_group, message)
            
            # Also send to item-specific group (for other users viewing same item)
            item_group = f"carousel_item_{item_id}"
            
            item_message = {
                'type': 'carousel_item_updated',
                'item_id': str(item_id),
                'changes': {'total_purchases': '+1'},  # Indicate increment
                'updated_fields': ['total_purchases'],
                'timestamp': timezone.now().isoformat()
            }
            
            async_to_sync(self.channel_layer.group_send)(item_group, item_message)
            
            logger.info(f"Sent purchase confirmation: user_id={user_id}, item_id={item_id}")
            
        except Exception as e:
            logger.error(f"Error sending purchase confirmation: {e}")
    
    def notify_new_item_available(self, item_id: str, item_title: str, 
                                target_users: List[int] = None):
        """
        Thông báo khi có item mới available
        
        Args:
            item_id: ID của item mới
            item_title: Title của item
            target_users: List user IDs cần thông báo (None = broadcast all)
        """
        try:
            if not self.channel_layer:
                return
            
            message = {
                'type': 'carousel_new_item_available',
                'item_id': str(item_id),
                'item_title': item_title,
                'timestamp': timezone.now().isoformat()
            }
            
            if target_users:
                # Send to specific users
                for user_id in target_users:
                    user_group = f"carousel_carousel_user_{user_id}"
                    async_to_sync(self.channel_layer.group_send)(user_group, message)
            else:
                # Broadcast to all anonymous users
                anonymous_group = "carousel_carousel_anonymous"
                async_to_sync(self.channel_layer.group_send)(anonymous_group, message)
            
            logger.info(f"Sent new item notification: item_id={item_id}, title={item_title}")
            
        except Exception as e:
            logger.error(f"Error sending new item notification: {e}")
    
    def notify_carousel_refresh(self, user_id: Optional[int] = None, 
                              device_type: str = 'desktop', limit: int = 20):
        """
        Thông báo carousel refresh
        
        Args:
            user_id: ID của user (None = all users)
            device_type: Type của device
            limit: Số lượng items
        """
        try:
            if not self.channel_layer:
                return
            
            message = {
                'type': 'carousel_refresh_triggered',
                'device_type': device_type,
                'limit': limit,
                'timestamp': timezone.now().isoformat()
            }
            
            if user_id:
                # Send to specific user
                user_group = f"carousel_carousel_user_{user_id}"
                async_to_sync(self.channel_layer.group_send)(user_group, message)
            else:
                # Send to all users and anonymous
                groups = ["carousel_carousel_anonymous"]
                # TODO: Add logic to send to all authenticated users
                
                for group in groups:
                    async_to_sync(self.channel_layer.group_send)(group, message)
            
            logger.info(f"Sent carousel refresh notification: user_id={user_id}")
            
        except Exception as e:
            logger.error(f"Error sending carousel refresh notification: {e}")
    
    def notify_stats_updated(self, stats: Dict[str, Any]):
        """
        Thông báo cập nhật stats cho admin dashboard
        
        Args:
            stats: Dictionary chứa stats data
        """
        try:
            if not self.channel_layer:
                return
            
            message = {
                'type': 'stats_updated',
                'stats': stats,
                'timestamp': timezone.now().isoformat()
            }
            
            # Send to admin stats group
            stats_group = "carousel_stats"
            async_to_sync(self.channel_layer.group_send)(stats_group, message)
            
            logger.info("Sent stats update notification")
            
        except Exception as e:
            logger.error(f"Error sending stats update notification: {e}")


# Global instance
realtime_service = CarouselRealtimeService()


# Helper functions cho easy usage
def notify_item_updated(item_id: str, changes: Dict[str, Any], updated_fields: List[str] = None):
    """Helper function để notify item updates"""
    realtime_service.notify_item_updated(item_id, changes, updated_fields)


def notify_purchase_confirmed(user_id: int, item_id: str, purchase_id: str):
    """Helper function để notify purchase confirmations"""
    realtime_service.notify_purchase_confirmed(user_id, item_id, purchase_id)


def notify_new_item_available(item_id: str, item_title: str, target_users: List[int] = None):
    """Helper function để notify new items"""
    realtime_service.notify_new_item_available(item_id, item_title, target_users)


def notify_carousel_refresh(user_id: Optional[int] = None, device_type: str = 'desktop', limit: int = 20):
    """Helper function để notify carousel refresh"""
    realtime_service.notify_carousel_refresh(user_id, device_type, limit)


def notify_stats_updated(stats: Dict[str, Any]):
    """Helper function để notify stats updates"""
    realtime_service.notify_stats_updated(stats)
