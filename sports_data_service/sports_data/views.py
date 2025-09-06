from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
import logging

from .models import Match, MatchEvent, Team, SportsDataProvider
from .serializers import (
    WebhookEventSerializer, LiveScoreUpdateSerializer,
    MatchEventCreateSerializer, MatchUpdateSerializer
)

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def webhook_event_handler(request):
    """
    Webhook endpoint để nhận sự kiện từ sports data provider
    """
    try:
        serializer = WebhookEventSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Invalid webhook data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Tìm trận đấu dựa trên external_id
        try:
            match = Match.objects.get(external_id=data['match_id'])
        except Match.DoesNotExist:
            logger.warning(f"Match not found for external_id: {data['match_id']}")
            return Response({
                'error': 'Match not found',
                'match_id': data['match_id']
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Tìm đội bóng
        try:
            team = Team.objects.get(external_id=data['team_id'])
        except Team.DoesNotExist:
            logger.warning(f"Team not found for external_id: {data['team_id']}")
            return Response({
                'error': 'Team not found',
                'team_id': data['team_id']
            }, status=status.HTTP_404_NOT_FOUND)
        
        with transaction.atomic():
            # Tạo sự kiện mới
            event = MatchEvent.objects.create(
                match=match,
                event_type=data['event_type'],
                minute=data['minute'],
                team=team,
                player_name=data.get('player_name', ''),
                description=data.get('description', ''),
                additional_data=data.get('additional_data', {}),
                requires_market_suspension=data.get('requires_suspension', False),
                suspension_duration=data.get('suspension_duration', 30)
            )
            
            # Kiểm tra xem có cần tạm dừng thị trường không
            if event.should_suspend_market():
                match.suspend_market(f"Sự kiện: {event.get_event_type_display()} - {event.description}")
                logger.info(f"Market suspended for match {match.id} due to {event.event_type}")
                
                # TODO: Gọi service để tạm dừng odds trong betting service
                # await suspend_betting_market(match.id, event.suspension_duration)
            
            logger.info(f"Webhook event processed: {event.event_type} for match {match.id}")
            
            return Response({
                'status': 'success',
                'event_id': event.id,
                'market_suspended': event.should_suspend_market()
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return Response({
            'error': 'Internal server error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def live_score_update(request):
    """
    Endpoint để cập nhật tỷ số trận đấu realtime
    """
    try:
        serializer = LiveScoreUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Invalid score data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        data = serializer.validated_data
        
        # Tìm trận đấu
        try:
            match = Match.objects.get(external_id=data['match_id'])
        except Match.DoesNotExist:
            logger.warning(f"Match not found for external_id: {data['match_id']}")
            return Response({
                'error': 'Match not found',
                'match_id': data['match_id']
            }, status=status.HTTP_404_NOT_FOUND)
        
        with transaction.atomic():
            # Cập nhật tỷ số
            old_score_home = match.score_home
            old_score_away = match.score_away
            
            match.score_home = data['score_home']
            match.score_away = data['score_away']
            match.current_minute = data['current_minute']
            
            # Cập nhật thống kê nếu có
            if 'possession_home' in data:
                match.possession_home = data['possession_home']
            if 'possession_away' in data:
                match.possession_away = data['possession_away']
            if 'shots_on_target_home' in data:
                match.shots_on_target_home = data['shots_on_target_home']
            if 'shots_on_target_away' in data:
                match.shots_on_target_away = data['shots_on_target_away']
            if 'corners_home' in data:
                match.corners_home = data['corners_home']
            if 'corners_away' in data:
                match.corners_away = data['corners_away']
            
            match.last_event_update = timezone.now()
            match.save()
            
            # Kiểm tra xem có bàn thắng mới không
            if (data['score_home'] > old_score_home or data['score_away'] > old_score_away):
                # Tự động tạm dừng thị trường khi có bàn thắng
                if not match.is_market_suspended:
                    match.suspend_market("Bàn thắng mới - Tạm dừng để cập nhật odds")
                    logger.info(f"Market suspended for match {match.id} due to new goal")
                    
                    # TODO: Gọi service để tạm dừng odds trong betting service
                    # await suspend_betting_market(match.id, 60)  # Tạm dừng 60 giây
            
            logger.info(f"Live score updated for match {match.id}: {data['score_home']}-{data['score_away']}")
            
            return Response({
                'status': 'success',
                'match_id': match.id,
                'score': f"{data['score_home']}-{data['score_away']}",
                'market_suspended': match.is_market_suspended
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        logger.error(f"Error updating live score: {str(e)}")
        return Response({
            'error': 'Internal server error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def match_events(request, match_id):
    """
    Lấy danh sách sự kiện của một trận đấu
    """
    try:
        match = Match.objects.get(id=match_id)
        events = match.events.all().order_by('minute', 'created_at')
        
        from .serializers import MatchEventSerializer
        serializer = MatchEventSerializer(events, many=True)
        
        return Response({
            'match_id': match_id,
            'events': serializer.data,
            'total_events': len(events)
        })
        
    except Match.DoesNotExist:
        return Response({
            'error': 'Match not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error fetching match events: {str(e)}")
        return Response({
            'error': 'Internal server error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def create_match_event(request):
    """
    Tạo sự kiện mới cho trận đấu (Admin only)
    """
    try:
        serializer = MatchEventCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'error': 'Invalid event data',
                'details': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        with transaction.atomic():
            event = serializer.save()
            
            # Kiểm tra xem có cần tạm dừng thị trường không
            if event.should_suspend_market():
                match = event.match
                if not match.is_market_suspended:
                    match.suspend_market(f"Sự kiện: {event.get_event_type_display()} - {event.description}")
                    logger.info(f"Market suspended for match {match.id} due to {event.event_type}")
            
            return Response({
                'status': 'success',
                'event_id': event.id,
                'market_suspended': event.should_suspend_market()
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        logger.error(f"Error creating match event: {str(e)}")
        return Response({
            'error': 'Internal server error',
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
