"""
WebSocket Consumers for Real-time Carousel Updates
Cost: $0 (Django Channels is free)
"""

import json
import logging
from typing import Dict, Any
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import FeaturedEvent, UserProductPurchase

logger = logging.getLogger('carousel')


class CarouselConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer cho real-time carousel updates
    """
    
    async def connect(self):
        """Kết nối WebSocket"""
        self.user = self.scope["user"]
        self.room_name = f"carousel_user_{self.user.id}" if self.user.is_authenticated else "carousel_anonymous"
        self.room_group_name = f"carousel_{self.room_name}"
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to carousel real-time updates',
            'user_authenticated': self.user.is_authenticated,
            'timestamp': timezone.now().isoformat(),
            'room': self.room_name
        }))
        
        logger.info(f"WebSocket connected: {self.room_name}")
    
    async def disconnect(self, close_code):
        """Ngắt kết nối WebSocket"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        logger.info(f"WebSocket disconnected: {self.room_name}, code: {close_code}")
    
    async def receive(self, text_data):
        """Nhận message từ WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe_to_item':
                await self.handle_subscribe_item(data)
            elif message_type == 'unsubscribe_from_item':
                await self.handle_unsubscribe_item(data)
            elif message_type == 'refresh_request':
                await self.handle_refresh_request(data)
            elif message_type == 'ping':
                await self.handle_ping()
            else:
                await self.send_error('Unknown message type')
                
        except json.JSONDecodeError:
            await self.send_error('Invalid JSON format')
        except Exception as e:
            logger.error(f"WebSocket receive error: {e}")
            await self.send_error('Internal error')
    
    async def handle_subscribe_item(self, data: Dict[str, Any]):
        """Đăng ký nhận updates cho item cụ thể"""
        item_id = data.get('item_id')
        if not item_id:
            await self.send_error('item_id is required')
            return
        
        # Join item-specific group
        item_group = f"carousel_item_{item_id}"
        await self.channel_layer.group_add(item_group, self.channel_name)
        
        await self.send(text_data=json.dumps({
            'type': 'subscription_success',
            'item_id': item_id,
            'message': f'Subscribed to updates for item {item_id}'
        }))
        
        logger.info(f"User {self.room_name} subscribed to item {item_id}")
    
    async def handle_unsubscribe_item(self, data: Dict[str, Any]):
        """Hủy đăng ký updates cho item"""
        item_id = data.get('item_id')
        if not item_id:
            await self.send_error('item_id is required')
            return
        
        # Leave item-specific group
        item_group = f"carousel_item_{item_id}"
        await self.channel_layer.group_discard(item_group, self.channel_name)
        
        await self.send(text_data=json.dumps({
            'type': 'unsubscription_success', 
            'item_id': item_id,
            'message': f'Unsubscribed from item {item_id}'
        }))
    
    async def handle_refresh_request(self, data: Dict[str, Any]):
        """Xử lý yêu cầu refresh từ client"""
        device_type = data.get('device_type', 'desktop')
        limit = data.get('limit', 20)
        
        # Trigger refresh for user's carousel
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'carousel_refresh_triggered',
                'device_type': device_type,
                'limit': limit,
                'timestamp': timezone.now().isoformat()
            }
        )
    
    async def handle_ping(self):
        """Xử lý ping để keep-alive"""
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'timestamp': timezone.now().isoformat()
        }))
    
    async def send_error(self, message: str):
        """Gửi error message"""
        await self.send(text_data=json.dumps({
            'type': 'error',
            'message': message,
            'timestamp': timezone.now().isoformat()
        }))
    
    # Handler methods cho các message types
    async def carousel_item_updated(self, event):
        """Xử lý khi carousel item được update"""
        await self.send(text_data=json.dumps({
            'type': 'item_updated',
            'item_id': event['item_id'],
            'changes': event.get('changes', {}),
            'updated_fields': event.get('updated_fields', []),
            'timestamp': event['timestamp']
        }))
    
    async def carousel_purchase_confirmed(self, event):
        """Xử lý khi purchase được confirm"""
        await self.send(text_data=json.dumps({
            'type': 'purchase_confirmed',
            'item_id': event['item_id'],
            'purchase_id': event['purchase_id'],
            'new_status': 'DA_MUA',
            'timestamp': event['timestamp']
        }))
    
    async def carousel_refresh_triggered(self, event):
        """Xử lý khi carousel refresh được trigger"""
        await self.send(text_data=json.dumps({
            'type': 'refresh_triggered',
            'device_type': event.get('device_type', 'desktop'),
            'limit': event.get('limit', 20),
            'message': 'Carousel refresh initiated',
            'timestamp': event['timestamp']
        }))
    
    async def carousel_new_item_available(self, event):
        """Xử lý khi có item mới available"""
        await self.send(text_data=json.dumps({
            'type': 'new_item_available',
            'item_id': event['item_id'],
            'item_title': event['item_title'],
            'message': 'New betting opportunity available!',
            'timestamp': event['timestamp']
        }))


class CarouselStatsConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer cho real-time carousel statistics
    Cho admin monitoring
    """
    
    async def connect(self):
        """Kết nối WebSocket cho stats"""
        self.user = self.scope["user"]
        
        # Chỉ cho phép admin users
        if not self.user.is_authenticated or not self.user.is_staff:
            await self.close()
            return
        
        self.room_group_name = "carousel_stats"
        
        # Join stats group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send current stats
        stats = await self.get_current_stats()
        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'stats': stats,
            'timestamp': timezone.now().isoformat()
        }))
    
    async def disconnect(self, close_code):
        """Ngắt kết nối stats WebSocket"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Nhận message từ stats WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'request_stats':
                stats = await self.get_current_stats()
                await self.send(text_data=json.dumps({
                    'type': 'stats_update',
                    'stats': stats,
                    'timestamp': timezone.now().isoformat()
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    @database_sync_to_async
    def get_current_stats(self) -> Dict[str, Any]:
        """Lấy stats hiện tại từ database"""
        try:
            # Get real-time statistics
            total_items = FeaturedEvent.objects.count()
            active_items = FeaturedEvent.objects.filter(is_active=True).count()
            total_purchases = UserProductPurchase.objects.count()
            pending_purchases = UserProductPurchase.objects.filter(status='PENDING').count()
            
            # Recent activity (last hour)
            from django.utils import timezone
            from datetime import timedelta
            last_hour = timezone.now() - timedelta(hours=1)
            
            recent_purchases = UserProductPurchase.objects.filter(
                purchased_at__gte=last_hour
            ).count()
            
            return {
                'items': {
                    'total': total_items,
                    'active': active_items,
                    'inactive': total_items - active_items
                },
                'purchases': {
                    'total': total_purchases,
                    'pending': pending_purchases,
                    'recent_hour': recent_purchases
                },
                'activity': {
                    'active_users': 0,  # TODO: Track active WebSocket connections
                    'total_connections': 0,  # TODO: Track connection count
                }
            }
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {'error': str(e)}
    
    # Handler methods
    async def stats_updated(self, event):
        """Xử lý khi stats được update"""
        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'stats': event['stats'],
            'timestamp': event['timestamp']
        }))
