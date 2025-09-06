"""
Kafka Consumers for Risk Management Service
Lắng nghe betting events để thực hiện risk assessment
Cost: $0 (Open source)
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'shared'))

from messaging.kafka_consumer_base import KafkaConsumerBase, EventRouter
from messaging.event_schemas import EventType
from typing import Dict, Any
import logging
from django.core.cache import cache
import time
import uuid

logger = logging.getLogger(__name__)


class BettingEventsConsumer(KafkaConsumerBase):
    """Consumer để nhận betting events và thực hiện risk assessment"""
    
    def __init__(self):
        super().__init__(
            topics=['betting_events'],
            consumer_group='risk_management_service',
            auto_offset_reset='earliest'
        )
        self.event_router = EventRouter()
        self._register_handlers()
    
    def _register_handlers(self):
        """Register event handlers"""
        self.event_router.register_handler(
            EventType.BET_PLACED,
            self._handle_bet_placed
        )
        self.event_router.register_handler(
            EventType.BET_UPDATED,
            self._handle_bet_updated
        )
        self.event_router.register_handler(
            EventType.BET_SETTLED,
            self._handle_bet_settled
        )
    
    def process_event(self, topic: str, key: str, event_data: Dict[str, Any]):
        """Process betting events"""
        self.event_router.route_event(event_data)
    
    def _handle_bet_placed(self, event_data: Dict[str, Any]):
        """Handle new bet placement - immediate risk assessment"""
        try:
            bet_id = event_data.get('bet_id')
            user_id = event_data.get('user_id')
            amount = event_data.get('amount', 0)
            odds = event_data.get('odds', 1.0)
            sport_id = event_data.get('sport_id')
            bet_type = event_data.get('bet_type')
            
            logger.info(f"Processing bet placement for risk assessment: {bet_id}")
            
            # Perform immediate risk assessment
            risk_assessment = self._assess_bet_risk(
                user_id, bet_id, amount, odds, sport_id, bet_type
            )
            
            # Store assessment result
            self._store_risk_assessment(bet_id, user_id, risk_assessment)
            
            # Trigger alerts if necessary
            if risk_assessment['risk_level'] in ['HIGH', 'CRITICAL']:
                self._trigger_risk_alert(user_id, risk_assessment)
            
            # Update user risk profile
            self._update_user_risk_profile(user_id, risk_assessment)
            
        except Exception as e:
            logger.error(f"Error handling bet placement: {e}")
            raise
    
    def _handle_bet_updated(self, event_data: Dict[str, Any]):
        """Handle bet updates - reassess if significant changes"""
        try:
            bet_id = event_data.get('bet_id')
            user_id = event_data.get('user_id')
            
            logger.info(f"Processing bet update for risk assessment: {bet_id}")
            
            # Check if update requires risk reassessment
            if self._requires_reassessment(event_data):
                # Perform new risk assessment
                risk_assessment = self._assess_bet_risk(
                    user_id, bet_id, 
                    event_data.get('amount', 0),
                    event_data.get('odds', 1.0),
                    event_data.get('sport_id'),
                    event_data.get('bet_type')
                )
                
                # Update stored assessment
                self._store_risk_assessment(bet_id, user_id, risk_assessment)
            
        except Exception as e:
            logger.error(f"Error handling bet update: {e}")
            raise
    
    def _handle_bet_settled(self, event_data: Dict[str, Any]):
        """Handle bet settlement - update risk models"""
        try:
            bet_id = event_data.get('bet_id')
            user_id = event_data.get('user_id')
            status = event_data.get('status')  # WON, LOST
            amount = event_data.get('amount', 0)
            
            logger.info(f"Processing bet settlement: {bet_id} - {status}")
            
            # Update user betting history for risk modeling
            self._update_betting_history(user_id, {
                'bet_id': bet_id,
                'status': status,
                'amount': amount,
                'settled_at': time.time()
            })
            
            # Check for problem gambling patterns
            self._check_problem_gambling_patterns(user_id)
            
            # Update fraud detection models
            self._update_fraud_models(user_id, event_data)
            
        except Exception as e:
            logger.error(f"Error handling bet settlement: {e}")
            raise
    
    def _assess_bet_risk(self, user_id: str, bet_id: str, amount: float, 
                        odds: float, sport_id: str, bet_type: str) -> Dict[str, Any]:
        """Perform comprehensive risk assessment"""
        try:
            assessment_id = str(uuid.uuid4())
            risk_factors = []
            risk_score = 0.0
            
            # 1. Amount-based risk
            amount_risk = self._assess_amount_risk(user_id, amount)
            risk_score += amount_risk['score']
            if amount_risk['factors']:
                risk_factors.extend(amount_risk['factors'])
            
            # 2. Odds-based risk
            odds_risk = self._assess_odds_risk(odds, sport_id)
            risk_score += odds_risk['score']
            if odds_risk['factors']:
                risk_factors.extend(odds_risk['factors'])
            
            # 3. User behavior risk
            behavior_risk = self._assess_user_behavior(user_id)
            risk_score += behavior_risk['score']
            if behavior_risk['factors']:
                risk_factors.extend(behavior_risk['factors'])
            
            # 4. Frequency risk
            frequency_risk = self._assess_betting_frequency(user_id)
            risk_score += frequency_risk['score']
            if frequency_risk['factors']:
                risk_factors.extend(frequency_risk['factors'])
            
            # 5. Pattern risk
            pattern_risk = self._assess_betting_patterns(user_id, bet_type, sport_id)
            risk_score += pattern_risk['score']
            if pattern_risk['factors']:
                risk_factors.extend(pattern_risk['factors'])
            
            # Determine risk level
            if risk_score >= 80:
                risk_level = 'CRITICAL'
            elif risk_score >= 60:
                risk_level = 'HIGH'
            elif risk_score >= 40:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            
            assessment = {
                'assessment_id': assessment_id,
                'user_id': user_id,
                'bet_id': bet_id,
                'risk_score': min(risk_score, 100),  # Cap at 100
                'risk_level': risk_level,
                'risk_factors': risk_factors,
                'action_required': risk_level in ['HIGH', 'CRITICAL'],
                'assessed_at': time.time()
            }
            
            logger.info(f"Risk assessment completed: {assessment_id} - {risk_level} ({risk_score:.1f})")
            return assessment
            
        except Exception as e:
            logger.error(f"Error in risk assessment: {e}")
            # Return safe default
            return {
                'assessment_id': str(uuid.uuid4()),
                'user_id': user_id,
                'bet_id': bet_id,
                'risk_score': 50.0,
                'risk_level': 'MEDIUM',
                'risk_factors': ['assessment_error'],
                'action_required': True,
                'assessed_at': time.time()
            }
    
    def _assess_amount_risk(self, user_id: str, amount: float) -> Dict[str, Any]:
        """Assess risk based on bet amount"""
        factors = []
        score = 0.0
        
        # Get user's betting history
        history_key = f"betting_history:{user_id}"
        history = cache.get(history_key, {'total_bet': 0, 'avg_bet': 0, 'max_bet': 0})
        
        avg_bet = history.get('avg_bet', 0)
        max_bet = history.get('max_bet', 0)
        
        # Large bet compared to history
        if avg_bet > 0 and amount > avg_bet * 5:
            factors.append('large_bet_vs_history')
            score += 20.0
        
        # Very large absolute amount
        if amount > 1000:
            factors.append('very_large_amount')
            score += 25.0
        elif amount > 500:
            factors.append('large_amount')
            score += 15.0
        
        # Sudden increase in bet size
        if max_bet > 0 and amount > max_bet * 2:
            factors.append('sudden_bet_increase')
            score += 15.0
        
        return {'score': score, 'factors': factors}
    
    def _assess_odds_risk(self, odds: float, sport_id: str) -> Dict[str, Any]:
        """Assess risk based on odds"""
        factors = []
        score = 0.0
        
        # Very high odds (longshot bets)
        if odds > 10.0:
            factors.append('very_high_odds')
            score += 20.0
        elif odds > 5.0:
            factors.append('high_odds')
            score += 10.0
        
        # Very low odds (sure bets - potential arbitrage)
        if odds < 1.2:
            factors.append('very_low_odds')
            score += 15.0
        
        # Sport-specific risk factors
        high_risk_sports = ['esports', 'virtual_sports', 'politics']
        if sport_id in high_risk_sports:
            factors.append('high_risk_sport')
            score += 10.0
        
        return {'score': score, 'factors': factors}
    
    def _assess_user_behavior(self, user_id: str) -> Dict[str, Any]:
        """Assess risk based on user behavior patterns"""
        factors = []
        score = 0.0
        
        # Check recent losses
        losses_key = f"recent_losses:{user_id}"
        recent_losses = cache.get(losses_key, 0)
        if recent_losses > 5:
            factors.append('consecutive_losses')
            score += 25.0
        elif recent_losses > 3:
            factors.append('multiple_losses')
            score += 15.0
        
        # Check betting time patterns (late night betting)
        current_hour = time.localtime().tm_hour
        if current_hour < 6 or current_hour > 23:
            factors.append('late_night_betting')
            score += 10.0
        
        # Check for rapid betting
        last_bet_key = f"last_bet_time:{user_id}"
        last_bet_time = cache.get(last_bet_key, 0)
        if last_bet_time and (time.time() - last_bet_time) < 300:  # 5 minutes
            factors.append('rapid_betting')
            score += 15.0
        
        return {'score': score, 'factors': factors}
    
    def _assess_betting_frequency(self, user_id: str) -> Dict[str, Any]:
        """Assess risk based on betting frequency"""
        factors = []
        score = 0.0
        
        # Count bets in last 24 hours
        today_key = f"bets_today:{user_id}"
        bets_today = cache.get(today_key, 0)
        
        if bets_today > 20:
            factors.append('excessive_daily_betting')
            score += 30.0
        elif bets_today > 10:
            factors.append('high_daily_betting')
            score += 20.0
        elif bets_today > 5:
            factors.append('moderate_daily_betting')
            score += 10.0
        
        # Count bets in last hour
        hour_key = f"bets_last_hour:{user_id}"
        bets_hour = cache.get(hour_key, 0)
        
        if bets_hour > 5:
            factors.append('excessive_hourly_betting')
            score += 20.0
        
        return {'score': score, 'factors': factors}
    
    def _assess_betting_patterns(self, user_id: str, bet_type: str, sport_id: str) -> Dict[str, Any]:
        """Assess risk based on betting patterns"""
        factors = []
        score = 0.0
        
        # Check for pattern changes
        pattern_key = f"betting_patterns:{user_id}"
        patterns = cache.get(pattern_key, {'sports': {}, 'types': {}})
        
        # Sudden change in preferred sport
        user_sports = patterns.get('sports', {})
        if user_sports and sport_id not in user_sports:
            factors.append('new_sport_betting')
            score += 5.0
        
        # High-risk bet types
        high_risk_types = ['system', 'accumulator', 'chain']
        if bet_type in high_risk_types:
            factors.append('high_risk_bet_type')
            score += 10.0
        
        return {'score': score, 'factors': factors}
    
    def _requires_reassessment(self, event_data: Dict[str, Any]) -> bool:
        """Check if bet update requires risk reassessment"""
        # Reassess if amount or odds changed significantly
        return ('amount' in event_data or 'odds' in event_data)
    
    def _store_risk_assessment(self, bet_id: str, user_id: str, assessment: Dict[str, Any]):
        """Store risk assessment result"""
        try:
            # Store assessment
            assessment_key = f"risk_assessment:{bet_id}"
            cache.set(assessment_key, assessment, timeout=86400)  # 24 hours
            
            # Update user risk history
            history_key = f"risk_history:{user_id}"
            history = cache.get(history_key, [])
            history.append({
                'assessment_id': assessment['assessment_id'],
                'risk_score': assessment['risk_score'],
                'risk_level': assessment['risk_level'],
                'timestamp': assessment['assessed_at']
            })
            
            # Keep only last 100 assessments
            if len(history) > 100:
                history = history[-100:]
            
            cache.set(history_key, history, timeout=86400 * 7)  # 7 days
            
        except Exception as e:
            logger.error(f"Error storing risk assessment: {e}")
    
    def _trigger_risk_alert(self, user_id: str, assessment: Dict[str, Any]):
        """Trigger risk alert for high-risk assessments"""
        try:
            alert_data = {
                'user_id': user_id,
                'assessment_id': assessment['assessment_id'],
                'risk_level': assessment['risk_level'],
                'risk_score': assessment['risk_score'],
                'factors': assessment['risk_factors'],
                'triggered_at': time.time()
            }
            
            # Store alert
            alert_key = f"risk_alert:{user_id}:{assessment['assessment_id']}"
            cache.set(alert_key, alert_data, timeout=86400)
            
            # Add to alerts queue for immediate processing
            alerts_queue_key = "risk_alerts_queue"
            alerts_queue = cache.get(alerts_queue_key, [])
            alerts_queue.append(alert_data)
            cache.set(alerts_queue_key, alerts_queue, timeout=3600)
            
            logger.warning(f"Risk alert triggered for user {user_id}: {assessment['risk_level']}")
            
        except Exception as e:
            logger.error(f"Error triggering risk alert: {e}")
    
    def _update_user_risk_profile(self, user_id: str, assessment: Dict[str, Any]):
        """Update user's overall risk profile"""
        try:
            profile_key = f"user_risk_profile:{user_id}"
            profile = cache.get(profile_key, {
                'average_risk_score': 0,
                'risk_assessments_count': 0,
                'high_risk_count': 0,
                'last_assessment': None
            })
            
            # Update statistics
            current_avg = profile.get('average_risk_score', 0)
            count = profile.get('risk_assessments_count', 0)
            new_score = assessment['risk_score']
            
            # Calculate new average
            new_avg = ((current_avg * count) + new_score) / (count + 1)
            
            profile.update({
                'average_risk_score': new_avg,
                'risk_assessments_count': count + 1,
                'last_assessment': assessment['assessed_at']
            })
            
            # Count high-risk assessments
            if assessment['risk_level'] in ['HIGH', 'CRITICAL']:
                profile['high_risk_count'] = profile.get('high_risk_count', 0) + 1
            
            cache.set(profile_key, profile, timeout=86400 * 30)  # 30 days
            
        except Exception as e:
            logger.error(f"Error updating user risk profile: {e}")
    
    def _update_betting_history(self, user_id: str, bet_data: Dict[str, Any]):
        """Update user betting history for risk modeling"""
        try:
            history_key = f"betting_history:{user_id}"
            history = cache.get(history_key, {
                'total_bets': 0,
                'total_amount': 0,
                'wins': 0,
                'losses': 0,
                'last_bets': []
            })
            
            # Update counters
            history['total_bets'] += 1
            history['total_amount'] += bet_data.get('amount', 0)
            
            if bet_data.get('status') == 'WON':
                history['wins'] += 1
            elif bet_data.get('status') == 'LOST':
                history['losses'] += 1
            
            # Add to recent bets
            history['last_bets'].append(bet_data)
            if len(history['last_bets']) > 50:  # Keep last 50 bets
                history['last_bets'] = history['last_bets'][-50:]
            
            cache.set(history_key, history, timeout=86400 * 30)  # 30 days
            
        except Exception as e:
            logger.error(f"Error updating betting history: {e}")
    
    def _check_problem_gambling_patterns(self, user_id: str):
        """Check for problem gambling indicators"""
        try:
            history_key = f"betting_history:{user_id}"
            history = cache.get(history_key, {})
            
            red_flags = []
            
            # Check loss streak
            recent_bets = history.get('last_bets', [])[-10:]  # Last 10 bets
            consecutive_losses = 0
            for bet in reversed(recent_bets):
                if bet.get('status') == 'LOST':
                    consecutive_losses += 1
                else:
                    break
            
            if consecutive_losses >= 7:
                red_flags.append('long_loss_streak')
            
            # Check win/loss ratio
            wins = history.get('wins', 0)
            losses = history.get('losses', 0)
            if losses > 0 and wins / max(losses, 1) < 0.2:  # Less than 20% win rate
                red_flags.append('poor_win_rate')
            
            # Check betting increase after losses
            if self._check_loss_chasing_pattern(recent_bets):
                red_flags.append('loss_chasing')
            
            if red_flags:
                self._flag_problem_gambling(user_id, red_flags)
            
        except Exception as e:
            logger.error(f"Error checking problem gambling patterns: {e}")
    
    def _check_loss_chasing_pattern(self, recent_bets: list) -> bool:
        """Check if user is chasing losses with bigger bets"""
        if len(recent_bets) < 5:
            return False
        
        for i in range(1, len(recent_bets)):
            current_bet = recent_bets[i]
            previous_bet = recent_bets[i-1]
            
            # If previous bet was a loss and current bet is significantly larger
            if (previous_bet.get('status') == 'LOST' and 
                current_bet.get('amount', 0) > previous_bet.get('amount', 0) * 1.5):
                return True
        
        return False
    
    def _flag_problem_gambling(self, user_id: str, red_flags: list):
        """Flag user for problem gambling"""
        try:
            flag_key = f"problem_gambling_flag:{user_id}"
            flag_data = {
                'flagged': True,
                'red_flags': red_flags,
                'flagged_at': time.time(),
                'requires_intervention': len(red_flags) >= 2
            }
            
            cache.set(flag_key, flag_data, timeout=86400 * 7)  # 7 days
            
            logger.warning(f"Problem gambling flagged for user {user_id}: {red_flags}")
            
        except Exception as e:
            logger.error(f"Error flagging problem gambling: {e}")
    
    def _update_fraud_models(self, user_id: str, event_data: Dict[str, Any]):
        """Update fraud detection models with new data"""
        try:
            # Simple fraud indicators tracking
            fraud_key = f"fraud_indicators:{user_id}"
            indicators = cache.get(fraud_key, {
                'unusual_patterns': 0,
                'suspicious_timing': 0,
                'last_update': time.time()
            })
            
            # Update timestamp
            indicators['last_update'] = time.time()
            
            cache.set(fraud_key, indicators, timeout=86400 * 7)  # 7 days
            
        except Exception as e:
            logger.error(f"Error updating fraud models: {e}")


# Consumer instance
betting_events_consumer = BettingEventsConsumer()


def start_risk_consumers():
    """Start all risk management consumers"""
    import threading
    
    consumer_thread = threading.Thread(target=betting_events_consumer.start, daemon=True)
    consumer_thread.start()
    
    logger.info("Started risk management consumers")
    return [betting_events_consumer]


def stop_risk_consumers():
    """Stop all risk management consumers"""
    betting_events_consumer.stop()
    logger.info("Stopped risk management consumers")
