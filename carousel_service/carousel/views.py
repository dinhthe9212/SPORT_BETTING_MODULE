from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from decimal import Decimal
from .models import FeaturedEvent
from .serializers import FeaturedEventSerializer
from .services import CarouselService, CarouselAutoRefreshService
from .realtime_service import notify_item_updated, notify_purchase_confirmed, notify_carousel_refresh

class FeaturedEventViewSet(viewsets.ModelViewSet):
    queryset = FeaturedEvent.objects.all()
    serializer_class = FeaturedEventSerializer
    
    def get_queryset(self):
        queryset = FeaturedEvent.objects.all()
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            is_active_bool = is_active.lower() == 'true'
            queryset = queryset.filter(is_active=is_active_bool)
        return queryset.order_by('order', '-created_at')
    
    @action(detail=False, methods=['get'])
    def prioritized(self, request):
        """Lấy danh sách carousel items đã được ưu tiên theo quy tắc business"""
        user = request.user if request.user.is_authenticated else None
        limit = int(request.query_params.get('limit', 20))
        device_type = request.query_params.get('device_type', 'desktop')
        
        items_data = CarouselService.get_carousel_items_with_status(
            user=user,
            limit=limit,
            device_type=device_type
        )
        
        return Response({
            'items': items_data,
            'display_count': CarouselService.get_display_count_by_device(device_type),
            'total_count': len(items_data),
            'device_type': device_type
        })
    
    @action(detail=False, methods=['get'])
    def randomized(self, request):
        """Lấy chuỗi sản phẩm ngẫu nhiên mới cho auto-refresh"""
        user = request.user if request.user.is_authenticated else None
        limit = int(request.query_params.get('limit', 20))
        device_type = request.query_params.get('device_type', 'desktop')
        
        items = CarouselService.get_randomized_items(
            user=user,
            limit=limit,
            device_type=device_type
        )
        
        items_data = []
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
                'purchase_status': item.get_purchase_status_for_user(user),
                'total_purchases': item.total_purchases,
            }
            items_data.append(item_data)
        
        # Send real-time notification về carousel refresh
        user_id = user.id if user and user.is_authenticated else None
        notify_carousel_refresh(
            user_id=user_id,
            device_type=device_type,
            limit=limit
        )
        
        return Response({
            'items': items_data,
            'refresh_interval': CarouselAutoRefreshService.get_refresh_interval(),
            'timestamp': request.META.get('timestamp')
        })
    
    @action(detail=True, methods=['post'])
    def purchase(self, request, pk=None):
        """Ghi nhận việc mua sản phẩm"""
        if not request.user.is_authenticated:
            return Response(
                {'error': 'Cần đăng nhập để mua sản phẩm'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        item = self.get_object()
        stake_amount = request.data.get('stake_amount')
        
        if not stake_amount:
            return Response(
                {'error': 'Thiếu thông tin số tiền cược'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            stake_amount = Decimal(str(stake_amount))
            if stake_amount < item.min_stake or stake_amount > item.max_stake:
                return Response(
                    {'error': f'Số tiền cược phải từ {item.min_stake} đến {item.max_stake}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Số tiền cược không hợp lệ'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        purchase = CarouselService.record_user_purchase(
            user=request.user,
            featured_event=item,
            stake_amount=stake_amount,
            odds_at_purchase=item.current_odds
        )
        
        # Send real-time notification về purchase
        notify_item_updated(
            item_id=str(item.id),
            changes={'total_purchases': item.total_purchases + 1},
            updated_fields=['total_purchases']
        )
        
        return Response({
            'message': 'Đã ghi nhận đơn hàng',
            'purchase_id': purchase.id,
            'status': purchase.status,
            'stake_amount': float(purchase.stake_amount),
            'odds_at_purchase': float(purchase.odds_at_purchase)
        })
    
    @action(detail=False, methods=['post'])
    def confirm_purchase(self, request):
        """Xác nhận đơn hàng (thường được gọi từ payment service)"""
        purchase_id = request.data.get('purchase_id')
        
        if not purchase_id:
            return Response(
                {'error': 'Thiếu purchase_id'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        purchase = CarouselService.confirm_purchase(purchase_id)
        
        if not purchase:
            return Response(
                {'error': 'Không tìm thấy đơn hàng'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Send real-time notification về purchase confirmation
        notify_purchase_confirmed(
            user_id=purchase.user.id,
            item_id=str(purchase.featured_event.id),
            purchase_id=str(purchase.id)
        )
        
        return Response({
            'message': 'Đã xác nhận đơn hàng',
            'purchase_id': purchase.id,
            'status': purchase.status,
            'featured_event_id': purchase.featured_event.id
        })
    
    @action(detail=True, methods=['patch'])
    def toggle_active(self, request, pk=None):
        item = self.get_object()
        item.is_active = not item.is_active
        item.save()
        serializer = self.get_serializer(item)
        return Response(serializer.data)
    
    @action(detail=False, methods=['patch'])
    def update_order(self, request):
        items_data = request.data.get('items', [])
        for item_data in items_data:
            item_id = item_data.get('id')
            new_order = item_data.get('order')
            if item_id and new_order is not None:
                try:
                    item = FeaturedEvent.objects.get(id=item_id)
                    item.order = new_order
                    item.save()
                except FeaturedEvent.DoesNotExist:
                    pass
        return Response({'message': 'Order updated successfully'})

