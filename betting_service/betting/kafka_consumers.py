"""
Kafka Consumers for Betting Service
Lắng nghe risk management và wallet events
Cost: $0 (Open source)
"""

import sys
import os
import time
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from messaging.kafka_consumer_base import KafkaConsumerBase, EventRouter
from messaging.event_schemas import EventType
from typing import Dict, Any
import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)


class RiskManagementConsumer(KafkaConsumerBase):
    """Consumer để nhận risk assessment results"""
    
    def __init__(self):
        super().__init__(
            topics=['risk_assessments'],
            consumer_group='betting_service_risk',
            auto_offset_reset='earliest'
        )
        self.event_router = EventRouter()
        self._register_handlers()
    
    def _register_handlers(self):
        """Register event handlers"""
        self.event_router.register_handler(
            EventType.RISK_ASSESSMENT_COMPLETED, 
            self._handle_risk_assessment
        )
        self.event_router.register_handler(
            EventType.RISK_ALERT_TRIGGERED,
            self._handle_risk_alert
        )
        self.event_router.register_handler(
            EventType.FRAUD_DETECTED,
            self._handle_fraud_detection
        )
    
    def process_event(self, topic: str, key: str, event_data: Dict[str, Any]):
        """Process risk management events"""
        self.event_router.route_event(event_data)
    
    def _handle_risk_assessment(self, event_data: Dict[str, Any]):
        """Handle risk assessment completion"""
        try:
            assessment_id = event_data.get('assessment_id')
            user_id = event_data.get('user_id')
            risk_score = event_data.get('risk_score', 0)
            risk_level = event_data.get('risk_level', 'LOW')
            action_required = event_data.get('action_required', False)
            
            logger.info(f"Risk assessment completed for user {user_id}: {risk_level} ({risk_score})")
            
            # Update pending bets based on risk assessment
            if action_required or risk_level in ['HIGH', 'CRITICAL']:
                self._handle_high_risk_user(user_id, risk_level, risk_score)
            
            # Cache risk score for future bet validation
            cache_key = f"user_risk_score:{user_id}"
            cache.set(cache_key, {
                'score': risk_score,
                'level': risk_level,
                'timestamp': event_data.get('timestamp')
            }, timeout=3600)  # 1 hour
            
        except Exception as e:
            logger.error(f"Error handling risk assessment: {e}")
            raise
    
    def _handle_risk_alert(self, event_data: Dict[str, Any]):
        """Handle risk alerts"""
        try:
            user_id = event_data.get('user_id')
            risk_level = event_data.get('risk_level')
            factors = event_data.get('factors', [])
            
            logger.warning(f"Risk alert for user {user_id}: {risk_level} - {factors}")
            
            # Temporarily suspend betting for high-risk users
            if risk_level in ['HIGH', 'CRITICAL']:
                self._suspend_user_betting(user_id, f"Risk alert: {risk_level}")
            
        except Exception as e:
            logger.error(f"Error handling risk alert: {e}")
            raise
    
    def _handle_fraud_detection(self, event_data: Dict[str, Any]):
        """Handle fraud detection"""
        try:
            user_id = event_data.get('user_id')
            factors = event_data.get('factors', [])
            
            logger.critical(f"Fraud detected for user {user_id}: {factors}")
            
            # Immediately suspend all betting activity
            self._suspend_user_betting(user_id, "Fraud detected")
            
            # Cancel all pending bets
            self._cancel_pending_bets(user_id, "Fraud detection")
            
        except Exception as e:
            logger.error(f"Error handling fraud detection: {e}")
            raise
    
    def _handle_high_risk_user(self, user_id: str, risk_level: str, risk_score: float):
        """Handle high-risk user betting restrictions"""
        try:
            # Reduce bet limits for high-risk users
            if risk_level == 'HIGH':
                max_bet_amount = 50.0  # $50 max
            elif risk_level == 'CRITICAL':
                max_bet_amount = 10.0  # $10 max
            else:
                return
            
            # Store betting restrictions
            cache_key = f"betting_restrictions:{user_id}"
            cache.set(cache_key, {
                'max_bet_amount': max_bet_amount,
                'risk_level': risk_level,
                'risk_score': risk_score,
                'restricted_at': time.time()
            }, timeout=86400)  # 24 hours
            
            logger.info(f"Applied betting restrictions for user {user_id}: max ${max_bet_amount}")
            
        except Exception as e:
            logger.error(f"Error applying betting restrictions: {e}")
    
    def _suspend_user_betting(self, user_id: str, reason: str):
        """Suspend user betting activity"""
        try:
            cache_key = f"betting_suspended:{user_id}"
            cache.set(cache_key, {
                'suspended': True,
                'reason': reason,
                'suspended_at': time.time()
            }, timeout=86400)  # 24 hours
            
            logger.warning(f"Suspended betting for user {user_id}: {reason}")
            
        except Exception as e:
            logger.error(f"Error suspending user betting: {e}")
    
    def _cancel_pending_bets(self, user_id: str, reason: str):
        """Cancel all pending bets for user"""
        try:
            # In real implementation, query database for pending bets
            # For now, just log the action
            logger.warning(f"Cancelling pending bets for user {user_id}: {reason}")
            
            # Update cache to track cancelled bets
            cache_key = f"cancelled_bets:{user_id}"
            current_count = cache.get(cache_key, 0)
            cache.set(cache_key, current_count + 1, timeout=3600)
            
        except Exception as e:
            logger.error(f"Error cancelling pending bets: {e}")


class WalletConsumer(KafkaConsumerBase):
    """Consumer để nhận wallet balance updates"""
    
    def __init__(self):
        super().__init__(
            topics=['wallet_events'],
            consumer_group='betting_service_wallet',
            auto_offset_reset='earliest'
        )
        self.event_router = EventRouter()
        self._register_handlers()
    
    def _register_handlers(self):
        """Register event handlers"""
        self.event_router.register_handler(
            EventType.BALANCE_UPDATED,
            self._handle_balance_update
        )
        self.event_router.register_handler(
            EventType.WALLET_DEPOSIT,
            self._handle_deposit_completed
        )
        self.event_router.register_handler(
            EventType.WALLET_WITHDRAWAL,
            self._handle_withdrawal_completed
        )
    
    def process_event(self, topic: str, key: str, event_data: Dict[str, Any]):
        """Process wallet events"""
        self.event_router.route_event(event_data)
    
    def _handle_balance_update(self, event_data: Dict[str, Any]):
        """Handle wallet balance updates"""
        try:
            user_id = event_data.get('user_id')
            balance_after = event_data.get('balance_after', 0)
            currency = event_data.get('currency', 'USD')
            
            # Update cached balance for betting validation
            cache_key = f"user_balance:{user_id}:{currency}"
            cache.set(cache_key, balance_after, timeout=1800)  # 30 minutes
            
            logger.info(f"Updated balance cache for user {user_id}: {balance_after} {currency}")
            
            # Check if user has pending bets that can now be placed
            self._check_pending_bets(user_id, balance_after, currency)
            
        except Exception as e:
            logger.error(f"Error handling balance update: {e}")
            raise
    
    def _handle_deposit_completed(self, event_data: Dict[str, Any]):
        """Handle successful deposits"""
        try:
            user_id = event_data.get('user_id')
            amount = event_data.get('amount', 0)
            currency = event_data.get('currency', 'USD')
            
            logger.info(f"Deposit completed for user {user_id}: {amount} {currency}")
            
            # Remove any deposit-related betting restrictions
            self._remove_insufficient_funds_restrictions(user_id)
            
            # Trigger bonus processing if applicable
            self._check_deposit_bonuses(user_id, amount, currency)
            
        except Exception as e:
            logger.error(f"Error handling deposit completion: {e}")
            raise
    
    def _handle_withdrawal_completed(self, event_data: Dict[str, Any]):
        """Handle successful withdrawals"""
        try:
            user_id = event_data.get('user_id')
            amount = event_data.get('amount', 0)
            currency = event_data.get('currency', 'USD')
            
            logger.info(f"Withdrawal completed for user {user_id}: {amount} {currency}")
            
            # Update withdrawal tracking for responsible gambling
            self._track_withdrawal_activity(user_id, amount, currency)
            
        except Exception as e:
            logger.error(f"Error handling withdrawal completion: {e}")
            raise
    
    def _check_pending_bets(self, user_id: str, balance: float, currency: str):
        """Check if pending bets can be placed with new balance"""
        try:
            cache_key = f"pending_bets:{user_id}"
            pending_bets = cache.get(cache_key, [])
            
            for bet_info in pending_bets:
                bet_amount = bet_info.get('amount', 0)
                if balance >= bet_amount:
                    logger.info(f"Sufficient balance for pending bet: {bet_info}")
                    # In real implementation, would trigger bet placement
            
        except Exception as e:
            logger.error(f"Error checking pending bets: {e}")
    
    def _remove_insufficient_funds_restrictions(self, user_id: str):
        """Remove betting restrictions due to insufficient funds"""
        try:
            cache_key = f"insufficient_funds:{user_id}"
            cache.delete(cache_key)
            logger.info(f"Removed insufficient funds restrictions for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error removing restrictions: {e}")
    
    def _check_deposit_bonuses(self, user_id: str, amount: float, currency: str):
        """Check for applicable deposit bonuses"""
        try:
            # Simple bonus logic - 10% bonus for deposits > $50
            if amount >= 50.0:
                bonus_amount = amount * 0.1
                
                cache_key = f"deposit_bonus:{user_id}"
                cache.set(cache_key, {
                    'bonus_amount': bonus_amount,
                    'currency': currency,
                    'deposit_amount': amount,
                    'created_at': time.time()
                }, timeout=86400)
                
                logger.info(f"Deposit bonus available for user {user_id}: {bonus_amount} {currency}")
            
        except Exception as e:
            logger.error(f"Error checking deposit bonuses: {e}")
    
    def _track_withdrawal_activity(self, user_id: str, amount: float, currency: str):
        """Track withdrawal activity for responsible gambling"""
        try:
            cache_key = f"withdrawal_tracking:{user_id}"
            current_data = cache.get(cache_key, {'total': 0, 'count': 0})
            
            current_data['total'] += amount
            current_data['count'] += 1
            current_data['last_withdrawal'] = time.time()
            
            cache.set(cache_key, current_data, timeout=86400 * 7)  # 7 days
            
            logger.info(f"Updated withdrawal tracking for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error tracking withdrawal activity: {e}")


# Consumer instances
risk_consumer = RiskManagementConsumer()
wallet_consumer = WalletConsumer()


def start_betting_consumers():
    """Start all betting service consumers"""
    import threading
    
    # Start consumers in separate threads
    risk_thread = threading.Thread(target=risk_consumer.start, daemon=True)
    wallet_thread = threading.Thread(target=wallet_consumer.start, daemon=True)
    
    risk_thread.start()
    wallet_thread.start()
    
    logger.info("Started all betting service consumers")
    
    return [risk_consumer, wallet_consumer]


def stop_betting_consumers():
    """Stop all betting service consumers"""
    risk_consumer.stop()
    wallet_consumer.stop()
    logger.info("Stopped all betting service consumers")
