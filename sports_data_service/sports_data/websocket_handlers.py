"""
WebSocket Handlers cho Real-time Sports Data
Tích hợp với Django Channels để push live updates
"""

import json
import asyncio
import logging
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import Match
from .providers.multi_sports_provider import MultiSportsDataProvider

logger = logging.getLogger(__name__)

class SportsDataWebSocketHandler:
    """
    Handler để push real-time sports data qua WebSocket
    """
    
    def __init__(self):
        self.channel_layer = get_channel_layer()
        self.sports_provider = MultiSportsDataProvider()
    
    async def push_live_scores(self, sport: str = None):
        """Push live scores to all connected clients"""
        try:
            # Get live scores from providers
            live_data = await self.get_live_scores_async(sport)
            
            if live_data and live_data.get('data'):
                message = {
                    'type': 'live_scores_update',
                    'sport': sport,
                    'data': live_data['data'],
                    'provider': live_data.get('provider'),
                    'timestamp': timezone.now().isoformat()
                }
                
                # Broadcast to all sports data subscribers
                await self.channel_layer.group_send(
                    'sports_data_live',
                    {
                        'type': 'sports_data_message',
                        'message': message
                    }
                )
                
                # Also send to sport-specific groups
                if sport:
                    await self.channel_layer.group_send(
                        f'sports_data_{sport.lower()}',
                        {
                            'type': 'sports_data_message', 
                            'message': message
                        }
                    )
                    
                logger.info(f"Pushed live scores for {sport} to WebSocket clients")
                
        except Exception as e:
            logger.error(f"Error pushing live scores: {e}")
    
    async def push_odds_update(self, sport: str, market: str = 'h2h'):
        """Push odds updates to connected clients"""
        try:
            odds_data = await self.get_odds_async(sport, market)
            
            if odds_data and odds_data.get('data'):
                message = {
                    'type': 'odds_update',
                    'sport': sport,
                    'market': market,
                    'data': odds_data['data'],
                    'provider': odds_data.get('provider'),
                    'timestamp': timezone.now().isoformat()
                }
                
                # Broadcast to odds subscribers
                await self.channel_layer.group_send(
                    'odds_updates',
                    {
                        'type': 'sports_data_message',
                        'message': message
                    }
                )
                
                logger.info(f"Pushed odds update for {sport}/{market}")
                
        except Exception as e:
            logger.error(f"Error pushing odds update: {e}")
    
    async def push_match_event(self, match_id: int, event_data: dict):
        """Push match events (goals, cards, etc.) instantly"""
        try:
            # Get match info
            match = await self.get_match_async(match_id)
            if not match:
                return
                
            message = {
                'type': 'match_event',
                'match_id': match_id,
                'sport': match.sport.name,
                'event_data': event_data,
                'timestamp': timezone.now().isoformat()
            }
            
            # Push to match-specific subscribers
            await self.channel_layer.group_send(
                f'match_{match_id}',
                {
                    'type': 'sports_data_message',
                    'message': message
                }
            )
            
            # Also push to sport subscribers
            await self.channel_layer.group_send(
                f'sports_data_{match.sport.name.lower()}',
                {
                    'type': 'sports_data_message',
                    'message': message
                }
            )
            
            logger.info(f"Pushed match event for match {match_id}")
            
        except Exception as e:
            logger.error(f"Error pushing match event: {e}")
    
    @database_sync_to_async
    def get_live_scores_async(self, sport: str):
        """Async wrapper for getting live scores"""
        return self.sports_provider.get_live_scores(sport)
    
    @database_sync_to_async  
    def get_odds_async(self, sport: str, market: str):
        """Async wrapper for getting odds"""
        return self.sports_provider.get_odds(sport, market)
    
    @database_sync_to_async
    def get_match_async(self, match_id: int):
        """Async wrapper for getting match"""
        try:
            return Match.objects.get(id=match_id)
        except Match.DoesNotExist:
            return None


class RealTimeDataPusher:
    """
    Background task để push data định kỳ
    """
    
    def __init__(self):
        self.handler = SportsDataWebSocketHandler()
        self.running = False
    
    async def start_live_data_push(self):
        """Start continuous live data pushing"""
        self.running = True
        logger.info("Started real-time data pusher")
        
        while self.running:
            try:
                # Push live scores every 30 seconds
                await self.push_all_live_sports()
                await asyncio.sleep(30)
                
                # Push odds every 60 seconds  
                await self.push_popular_odds()
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in live data push loop: {e}")
                await asyncio.sleep(10)  # Short sleep on error
    
    async def push_all_live_sports(self):
        """Push live data for all popular sports"""
        popular_sports = ['football', 'basketball', 'tennis', 'baseball']
        
        for sport in popular_sports:
            try:
                await self.handler.push_live_scores(sport)
                await asyncio.sleep(2)  # Small delay between sports
            except Exception as e:
                logger.error(f"Error pushing live data for {sport}: {e}")
    
    async def push_popular_odds(self):
        """Push odds for popular sports"""
        popular_sports = ['football', 'basketball', 'tennis']
        
        for sport in popular_sports:
            try:
                await self.handler.push_odds_update(sport, 'h2h')
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Error pushing odds for {sport}: {e}")
    
    def stop(self):
        """Stop the pusher"""
        self.running = False
        logger.info("Stopped real-time data pusher")


# WebSocket Consumer for Sports Data
from channels.generic.websocket import AsyncWebsocketConsumer

class SportsDataConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer cho sports data subscriptions
    """
    
    async def connect(self):
        """Handle connection"""
        # Join general sports data group
        await self.channel_layer.group_add(
            'sports_data_live',
            self.channel_name
        )
        
        await self.accept()
        
        # Send welcome message
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to sports data stream'
        }))
    
    async def disconnect(self, close_code):
        """Handle disconnection"""
        # Leave all groups
        await self.channel_layer.group_discard(
            'sports_data_live',
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe_sport':
                sport = data.get('sport')
                if sport:
                    await self.channel_layer.group_add(
                        f'sports_data_{sport.lower()}',
                        self.channel_name
                    )
                    await self.send(text_data=json.dumps({
                        'type': 'subscription_confirmed',
                        'sport': sport
                    }))
            
            elif message_type == 'subscribe_match':
                match_id = data.get('match_id')
                if match_id:
                    await self.channel_layer.group_add(
                        f'match_{match_id}',
                        self.channel_name
                    )
                    await self.send(text_data=json.dumps({
                        'type': 'match_subscription_confirmed',
                        'match_id': match_id
                    }))
            
            elif message_type == 'subscribe_odds':
                await self.channel_layer.group_add(
                    'odds_updates',
                    self.channel_name
                )
                await self.send(text_data=json.dumps({
                    'type': 'odds_subscription_confirmed'
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
    
    async def sports_data_message(self, event):
        """Handle sports data messages from group"""
        message = event['message']
        
        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))


# Usage trong Django management command
"""
# Create management command: management/commands/start_realtime_pusher.py

from django.core.management.base import BaseCommand
import asyncio
from sports_data.websocket_handlers import RealTimeDataPusher

class Command(BaseCommand):
    help = 'Start real-time sports data pusher'
    
    def handle(self, *args, **options):
        pusher = RealTimeDataPusher()
        
        try:
            asyncio.run(pusher.start_live_data_push())
        except KeyboardInterrupt:
            pusher.stop()
            self.stdout.write("Stopped real-time pusher")
"""
