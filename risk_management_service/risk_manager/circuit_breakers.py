"""
Advanced Circuit Breakers for Risk Management
Rule-based triggers thay vì ML để tiết kiệm chi phí
"""

import logging
import uuid
from datetime import timedelta
from typing import Dict, List, Any
from decimal import Decimal
from enum import Enum
from django.db import models, transaction
from django.db.models import Sum
from django.utils import timezone
from django.core.cache import cache
from django.conf import settings
import requests
from .models import RiskAlert, RiskAuditLog
from .services import TradingSuspensionService

logger = logging.getLogger(__name__)

class TriggerType(Enum):
    """Types of circuit breaker triggers"""
    VOLUME_SPIKE = "volume_spike"
    LIABILITY_THRESHOLD = "liability_threshold" 
    ODDS_VOLATILITY = "odds_volatility"
    PATTERN_DETECTION = "pattern_detection"
    TIME_BASED = "time_based"
    COMBINATION = "combination"

class SeverityLevel(Enum):
    """Severity levels for circuit breaker actions"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CircuitBreakerRule(models.Model):
    """
    Configurable rules cho circuit breakers
    Rule-based thay vì ML để tiết kiệm chi phí
    """
    
    TRIGGER_TYPES = [
        ('VOLUME_SPIKE', 'Volume Spike Detection'),
        ('LIABILITY_THRESHOLD', 'Liability Threshold Breach'),
        ('ODDS_VOLATILITY', 'Odds Volatility Alert'),
        ('PATTERN_DETECTION', 'Suspicious Pattern'),
        ('TIME_BASED', 'Time-based Rule'),
        ('COMBINATION', 'Combination Rule'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Low Priority'),
        ('MEDIUM', 'Medium Priority'),
        ('HIGH', 'High Priority'),
        ('CRITICAL', 'Critical - Immediate Action'),
    ]
    
    ACTIONS = [
        ('LOG_ONLY', 'Log Only'),
        ('ALERT', 'Send Alert'),
        ('SUSPEND_MARKET', 'Suspend Market'),
        ('SUSPEND_SPORT', 'Suspend Sport'),
        ('REDUCE_LIMITS', 'Reduce Limits'),
        ('EMERGENCY_STOP', 'Emergency Stop All'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Rule configuration
    trigger_type = models.CharField(max_length=50, choices=TRIGGER_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    action = models.CharField(max_length=50, choices=ACTIONS)
    
    # Targeting
    target_sports = models.JSONField(default=list, blank=True, help_text='Specific sports to monitor')
    target_bet_types = models.JSONField(default=list, blank=True, help_text='Specific bet types to monitor')
    global_rule = models.BooleanField(default=False, help_text='Apply to all sports/bet types')
    
    # Rule parameters (JSON configuration)
    rule_parameters = models.JSONField(default=dict, help_text='Specific parameters for this rule')
    
    # Rule status
    is_active = models.BooleanField(default=True)
    triggered_count = models.IntegerField(default=0)
    last_triggered = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-severity', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.severity})"


class CircuitBreakerEvent(models.Model):
    """Log của circuit breaker triggers và actions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule = models.ForeignKey(CircuitBreakerRule, on_delete=models.CASCADE, related_name='events')
    
    # Event details
    triggered_at = models.DateTimeField(auto_now_add=True)
    trigger_data = models.JSONField(help_text='Data that triggered the rule')
    action_taken = models.CharField(max_length=50)
    
    # Context
    sport_name = models.CharField(max_length=100, blank=True, null=True)
    bet_type_id = models.IntegerField(blank=True, null=True)
    match_id = models.IntegerField(blank=True, null=True)
    
    # Results
    suspension_id = models.UUIDField(blank=True, null=True, help_text='ID of created suspension')
    alert_id = models.UUIDField(blank=True, null=True, help_text='ID of created alert')
    
    # Event metadata
    metadata = models.JSONField(default=dict)
    
    class Meta:
        ordering = ['-triggered_at']


class AdvancedCircuitBreaker:
    """
    Advanced circuit breaker với rule-based triggers
    Không cần ML - sử dụng statistical thresholds và patterns
    """
    
    def __init__(self):
        self.cache_timeout = 300  # 5 minutes cache
    
    def check_all_rules(self) -> List[Dict[str, Any]]:
        """Check tất cả active rules và trigger nếu cần"""
        active_rules = CircuitBreakerRule.objects.filter(is_active=True)
        triggered_rules = []
        
        for rule in active_rules:
            try:
                trigger_result = self._check_rule(rule)
                if trigger_result['triggered']:
                    triggered_rules.append({
                        'rule': rule,
                        'result': trigger_result,
                        'action_taken': self._execute_rule_action(rule, trigger_result)
                    })
            except Exception as e:
                logger.error(f"Error checking rule {rule.id}: {e}")
        
        return triggered_rules
    
    def _check_rule(self, rule: CircuitBreakerRule) -> Dict[str, Any]:
        """Check individual rule"""
        
        if rule.trigger_type == 'VOLUME_SPIKE':
            return self._check_volume_spike(rule)
        elif rule.trigger_type == 'LIABILITY_THRESHOLD':
            return self._check_liability_threshold(rule)
        elif rule.trigger_type == 'ODDS_VOLATILITY':
            return self._check_odds_volatility(rule)
        elif rule.trigger_type == 'PATTERN_DETECTION':
            return self._check_pattern_detection(rule)
        elif rule.trigger_type == 'TIME_BASED':
            return self._check_time_based(rule)
        elif rule.trigger_type == 'COMBINATION':
            return self._check_combination_rule(rule)
        
        return {'triggered': False, 'reason': 'Unknown rule type'}
    
    def _check_volume_spike(self, rule: CircuitBreakerRule) -> Dict[str, Any]:
        """
        Check cho volume spike
        Detect abnormal betting volume compared to historical averages
        """
        params = rule.rule_parameters
        
        # Default parameters
        spike_threshold = params.get('spike_threshold', 3.0)  # 3x normal volume
        time_window = params.get('time_window', 60)  # 60 minutes
        comparison_period = params.get('comparison_period', 7)  # 7 days historical
        
        current_time = timezone.now()
        window_start = current_time - timedelta(minutes=time_window)
        
        # Get current volume
        current_volume = self._get_betting_volume(
            start_time=window_start,
            end_time=current_time,
            sports=rule.target_sports,
            bet_types=rule.target_bet_types
        )
        
        # Get historical average
        historical_start = current_time - timedelta(days=comparison_period)
        historical_volume = self._get_average_volume(
            start_time=historical_start,
            end_time=current_time - timedelta(hours=1),  # Exclude current hour
            window_minutes=time_window,
            sports=rule.target_sports,
            bet_types=rule.target_bet_types
        )
        
        if historical_volume > 0:
            spike_ratio = current_volume / historical_volume
            
            if spike_ratio >= spike_threshold:
                return {
                    'triggered': True,
                    'reason': f'Volume spike detected: {spike_ratio:.2f}x normal',
                    'data': {
                        'current_volume': float(current_volume),
                        'historical_average': float(historical_volume),
                        'spike_ratio': float(spike_ratio),
                        'threshold': spike_threshold
                    }
                }
        
        return {'triggered': False, 'reason': 'Volume within normal range'}
    
    def _check_liability_threshold(self, rule: CircuitBreakerRule) -> Dict[str, Any]:
        """
        Check liability thresholds
        Monitor total exposure limits
        """
        params = rule.rule_parameters
        
        # Default parameters
        threshold_percentage = params.get('threshold_percentage', 80.0)  # 80% of limit
        check_scope = params.get('scope', 'sport')  # 'sport', 'bet_type', or 'global'
        
        liability_data = self._get_current_liability(
            scope=check_scope,
            sports=rule.target_sports,
            bet_types=rule.target_bet_types
        )
        
        for item in liability_data:
            exposure_percentage = item['exposure_percentage']
            
            if exposure_percentage >= threshold_percentage:
                return {
                    'triggered': True,
                    'reason': f'Liability threshold exceeded: {exposure_percentage:.1f}%',
                    'data': {
                        'scope': check_scope,
                        'item': item,
                        'threshold': threshold_percentage
                    }
                }
        
        return {'triggered': False, 'reason': 'Liability within acceptable limits'}
    
    def _check_odds_volatility(self, rule: CircuitBreakerRule) -> Dict[str, Any]:
        """
        Check odds volatility
        Detect rapid odds changes that might indicate market manipulation
        """
        params = rule.rule_parameters
        
        # Default parameters
        volatility_threshold = params.get('volatility_threshold', 20.0)  # 20% change
        time_window = params.get('time_window', 15)  # 15 minutes
        change_frequency = params.get('change_frequency', 5)  # 5 changes in window
        
        current_time = timezone.now()
        window_start = current_time - timedelta(minutes=time_window)
        
        volatile_odds = self._get_volatile_odds(
            start_time=window_start,
            end_time=current_time,
            volatility_threshold=volatility_threshold,
            change_frequency=change_frequency,
            sports=rule.target_sports,
            bet_types=rule.target_bet_types
        )
        
        if volatile_odds:
            return {
                'triggered': True,
                'reason': f'High odds volatility detected: {len(volatile_odds)} markets',
                'data': {
                    'volatile_markets': volatile_odds,
                    'threshold': volatility_threshold,
                    'time_window': time_window
                }
            }
        
        return {'triggered': False, 'reason': 'Odds volatility within normal range'}
    
    def _check_pattern_detection(self, rule: CircuitBreakerRule) -> Dict[str, Any]:
        """
        Check cho suspicious betting patterns
        Rule-based pattern detection (không cần ML)
        """
        params = rule.rule_parameters
        
        pattern_type = params.get('pattern_type', 'coordinated_betting')
        
        if pattern_type == 'coordinated_betting':
            return self._check_coordinated_betting(rule, params)
        elif pattern_type == 'late_heavy_betting':
            return self._check_late_heavy_betting(rule, params)
        elif pattern_type == 'arbitrage_attempt':
            return self._check_arbitrage_attempt(rule, params)
        
        return {'triggered': False, 'reason': f'Unknown pattern type: {pattern_type}'}
    
    def _check_coordinated_betting(self, rule: CircuitBreakerRule, params: Dict) -> Dict[str, Any]:
        """Check for coordinated betting patterns"""
        
        # Parameters
        user_threshold = params.get('user_threshold', 10)  # 10+ users
        time_window = params.get('time_window', 30)  # 30 minutes
        amount_similarity = params.get('amount_similarity', 0.1)  # 10% variance
        
        current_time = timezone.now()
        window_start = current_time - timedelta(minutes=time_window)
        
        # Get recent bets
        suspicious_groups = self._find_coordinated_bets(
            start_time=window_start,
            end_time=current_time,
            user_threshold=user_threshold,
            amount_similarity=amount_similarity,
            sports=rule.target_sports,
            bet_types=rule.target_bet_types
        )
        
        if suspicious_groups:
            return {
                'triggered': True,
                'reason': f'Coordinated betting detected: {len(suspicious_groups)} groups',
                'data': {
                    'suspicious_groups': suspicious_groups,
                    'user_threshold': user_threshold,
                    'time_window': time_window
                }
            }
        
        return {'triggered': False, 'reason': 'No coordinated betting patterns detected'}
    
    def _check_late_heavy_betting(self, rule: CircuitBreakerRule, params: Dict) -> Dict[str, Any]:
        """Check for late heavy betting patterns"""
        
        # Parameters
        time_threshold = params.get('time_threshold', 10)  # 10 minutes before event
        amount_threshold = params.get('amount_threshold', 10000)  # $10k+ bets
        user_threshold = params.get('user_threshold', 5)  # 5+ users
        
        current_time = timezone.now()
        
        # Mock implementation - replace with actual betting data query
        late_bets = self._get_late_heavy_bets(
            time_threshold=time_threshold,
            amount_threshold=amount_threshold,
            user_threshold=user_threshold,
            sports=rule.target_sports,
            bet_types=rule.target_bet_types
        )
        
        if late_bets:
            return {
                'triggered': True,
                'reason': f'Late heavy betting detected: {len(late_bets)} suspicious bets',
                'data': {
                    'late_bets': late_bets,
                    'time_threshold': time_threshold,
                    'amount_threshold': amount_threshold
                }
            }
        
        return {'triggered': False, 'reason': 'No late heavy betting patterns detected'}
    
    def _check_arbitrage_attempt(self, rule: CircuitBreakerRule, params: Dict) -> Dict[str, Any]:
        """Check for arbitrage betting attempts"""
        
        # Parameters
        profit_threshold = params.get('profit_threshold', 0.05)  # 5% guaranteed profit
        time_window = params.get('time_window', 15)  # 15 minutes
        
        current_time = timezone.now()
        window_start = current_time - timedelta(minutes=time_window)
        
        arbitrage_attempts = self._find_arbitrage_attempts(
            start_time=window_start,
            end_time=current_time,
            profit_threshold=profit_threshold,
            sports=rule.target_sports,
            bet_types=rule.target_bet_types
        )
        
        if arbitrage_attempts:
            return {
                'triggered': True,
                'reason': f'Arbitrage attempts detected: {len(arbitrage_attempts)} cases',
                'data': {
                    'arbitrage_attempts': arbitrage_attempts,
                    'profit_threshold': profit_threshold,
                    'time_window': time_window
                }
            }
        
        return {'triggered': False, 'reason': 'No arbitrage attempts detected'}
    
    def _check_time_based(self, rule: CircuitBreakerRule) -> Dict[str, Any]:
        """
        Time-based rules (market close, peak hours, etc.)
        """
        params = rule.rule_parameters
        
        trigger_times = params.get('trigger_times', [])  # List of trigger conditions
        current_time = timezone.now()
        
        for trigger in trigger_times:
            if self._time_condition_met(current_time, trigger):
                return {
                    'triggered': True,
                    'reason': f'Time-based trigger: {trigger["description"]}',
                    'data': {
                        'trigger_condition': trigger,
                        'current_time': current_time.isoformat()
                    }
                }
        
        return {'triggered': False, 'reason': 'No time conditions met'}
    
    def _check_combination_rule(self, rule: CircuitBreakerRule) -> Dict[str, Any]:
        """Check combination of multiple conditions"""
        
        params = rule.rule_parameters
        conditions = params.get('conditions', [])
        required_conditions = params.get('required_conditions', len(conditions))
        
        triggered_conditions = []
        
        for condition in conditions:
            condition_result = self._check_single_condition(condition)
            if condition_result['triggered']:
                triggered_conditions.append(condition_result)
        
        if len(triggered_conditions) >= required_conditions:
            return {
                'triggered': True,
                'reason': f'Combination rule triggered: {len(triggered_conditions)}/{required_conditions} conditions met',
                'data': {
                    'triggered_conditions': triggered_conditions,
                    'required_conditions': required_conditions,
                    'total_conditions': len(conditions)
                }
            }
        
        return {'triggered': False, 'reason': 'Combination rule conditions not met'}
    
    def _execute_rule_action(self, rule: CircuitBreakerRule, trigger_result: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action khi rule triggered"""
        
        action_result = {'action': rule.action, 'success': False}
        
        try:
            with transaction.atomic():
                # Log event
                event = CircuitBreakerEvent.objects.create(
                    rule=rule,
                    trigger_data=trigger_result['data'],
                    action_taken=rule.action,
                    sport_name=trigger_result.get('sport_name'),
                    bet_type_id=trigger_result.get('bet_type_id'),
                    match_id=trigger_result.get('match_id')
                )
                
                # Execute specific action
                if rule.action == 'LOG_ONLY':
                    action_result['success'] = True
                    
                elif rule.action == 'ALERT':
                    alert = self._create_alert(rule, trigger_result, event)
                    event.alert_id = alert.id
                    action_result['alert_id'] = str(alert.id)
                    action_result['success'] = True
                    
                elif rule.action == 'SUSPEND_MARKET':
                    suspension = self._suspend_market(rule, trigger_result, event)
                    event.suspension_id = suspension.id
                    action_result['suspension_id'] = str(suspension.id)
                    action_result['success'] = True
                    
                elif rule.action == 'SUSPEND_SPORT':
                    suspension = self._suspend_sport(rule, trigger_result, event)
                    event.suspension_id = suspension.id
                    action_result['suspension_id'] = str(suspension.id)
                    action_result['success'] = True
                    
                elif rule.action == 'REDUCE_LIMITS':
                    limit_result = self._reduce_limits(rule, trigger_result, event)
                    action_result.update(limit_result)
                    action_result['success'] = True
                    
                elif rule.action == 'EMERGENCY_STOP':
                    stop_result = self._emergency_stop_all(rule, trigger_result, event)
                    action_result.update(stop_result)
                    action_result['success'] = True
                
                # Update rule stats
                rule.triggered_count += 1
                rule.last_triggered = timezone.now()
                rule.save()
                
                event.save()
                
                logger.warning(f"Circuit breaker triggered: {rule.name} - Action: {rule.action}")
                
        except Exception as e:
            logger.error(f"Error executing circuit breaker action: {e}")
            action_result['error'] = str(e)
        
        return action_result
    
    def _create_alert(self, rule: CircuitBreakerRule, trigger_result: Dict, event: CircuitBreakerEvent):
        """Create risk alert"""
        return RiskAlert.objects.create(
            alert_type='CIRCUIT_BREAKER',
            severity=rule.severity,
            title=f"Circuit Breaker: {rule.name}",
            message=trigger_result['reason'],
            related_data={
                'rule_id': str(rule.id),
                'event_id': str(event.id),
                'trigger_data': trigger_result['data']
            }
        )
    
    def _suspend_sport(self, rule: CircuitBreakerRule, trigger_result: Dict, event: CircuitBreakerEvent):
        """Suspend sport trading"""
        
        sport_name = trigger_result.get('sport_name') or (
            rule.target_sports[0] if rule.target_sports else 'ALL'
        )
        
        return TradingSuspensionService().suspend_trading(
            suspension_type='SPORT_SPECIFIC',
            reason='RISK_MANAGEMENT',
            description=f"Automatic suspension by circuit breaker: {rule.name}. {trigger_result['reason']}",
            sport_id=sport_name,
            suspended_by='CIRCUIT_BREAKER'
        )
    
    def _suspend_market(self, rule: CircuitBreakerRule, trigger_result: Dict, event: CircuitBreakerEvent):
        """Suspend specific market trading"""
        
        market_id = trigger_result.get('market_id') or 'UNKNOWN'
        
        return TradingSuspensionService().suspend_trading(
            suspension_type='MARKET_SPECIFIC',
            reason='RISK_MANAGEMENT',
            description=f"Automatic market suspension by circuit breaker: {rule.name}. {trigger_result['reason']}",
            market_identifier=market_id,
            suspended_by='CIRCUIT_BREAKER'
        )
    
    def _reduce_limits(self, rule: CircuitBreakerRule, trigger_result: Dict, event: CircuitBreakerEvent):
        """Reduce betting limits"""
        
        params = rule.rule_parameters
        reduction_percentage = params.get('reduction_percentage', 50)  # 50% reduction
        
        # Mock implementation - replace with actual limit reduction logic
        return {
            'limits_reduced': True,
            'reduction_percentage': reduction_percentage,
            'affected_sports': rule.target_sports or ['ALL'],
            'affected_bet_types': rule.target_bet_types or ['ALL']
        }
    
    def _emergency_stop_all(self, rule: CircuitBreakerRule, trigger_result: Dict, event: CircuitBreakerEvent):
        """Emergency stop all trading"""
        
        # Suspend all sports
        all_sports_suspension = TradingSuspensionService().suspend_trading(
            suspension_type='GLOBAL',
            reason='EMERGENCY_STOP',
            description=f"EMERGENCY STOP by circuit breaker: {rule.name}. {trigger_result['reason']}",
            suspended_by='CIRCUIT_BREAKER'
        )
        
        return {
            'emergency_stop_activated': True,
            'global_suspension_id': str(all_sports_suspension.id),
            'affected_scope': 'ALL_TRADING',
            'stop_reason': trigger_result['reason']
        }
    
    # Helper methods cho data collection
    def _get_betting_volume(self, start_time, end_time, sports=None, bet_types=None) -> Decimal:
        """Get betting volume trong time period"""
        # Tạo cache key với filters
        filters = []
        if sports:
            filters.extend(sports)
        if bet_types:
            filters.extend(bet_types)
        
        cache_key = f"betting_volume_{start_time.isoformat()}_{end_time.isoformat()}_{'_'.join(filters) if filters else 'all'}"
        cached_volume = cache.get(cache_key)
        
        if cached_volume is not None:
            return Decimal(str(cached_volume))
        
        # Query database để lấy betting volume thực tế
        try:
            # Thử import BetSlip từ Betting Service
            from betting.models import BetSlip
            
            # Tạo filter query
            volume_query = BetSlip.objects.filter(
                created_at__gte=start_time,
                created_at__lt=end_time,
                status__in=['ACTIVE', 'PENDING', 'WON', 'LOST']
            )
            
            # Áp dụng filters nếu có
            if sports:
                volume_query = volume_query.filter(sport_id__in=sports)
            if bet_types:
                volume_query = volume_query.filter(bet_type_id__in=bet_types)
            
            # Tính tổng volume
            total_volume = volume_query.aggregate(
                total_volume=Sum('total_stake')
            )['total_volume'] or Decimal('0.00')
            
            # Cache kết quả trong 10 phút
            cache.set(cache_key, float(total_volume), 600)
            
            return Decimal(str(total_volume))
            
        except ImportError:
            # Fallback: Gọi API từ Betting Service
            try:
                params = {
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat()
                }
                if sports:
                    params['sports'] = ','.join(sports)
                if bet_types:
                    params['bet_types'] = ','.join(bet_types)
                
                response = requests.get(
                    f"{getattr(settings, 'BETTING_SERVICE_URL', 'http://betting-service:8000')}/api/analytics/betting-volume/",
                    params=params,
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    total_volume = Decimal(str(data.get('total_volume', '0.00')))
                    
                    # Cache kết quả trong 10 phút
                    cache.set(cache_key, float(total_volume), 600)
                    return total_volume
                    
            except Exception as api_error:
                logger.warning(f"API call failed for betting volume: {api_error}")
            
            # Fallback cuối cùng: Sử dụng RiskAuditLog để ước tính
            try:
                audit_query = RiskAuditLog.objects.filter(
                    action_type='BET_PLACED',
                    created_at__gte=start_time,
                    created_at__lt=end_time
                )
                
                if sports:
                    audit_query = audit_query.filter(
                        action_details__sport_id__in=sports
                    )
                if bet_types:
                    audit_query = audit_query.filter(
                        action_details__bet_type_id__in=bet_types
                    )
                
                # Đếm số lượng bets và ước tính volume
                bet_count = audit_query.count()
                estimated_volume = bet_count * Decimal('50.00')  # Giả sử trung bình $50/bet
                
                # Cache kết quả ước tính trong 5 phút
                cache.set(cache_key, float(estimated_volume), 300)
                return estimated_volume
                
            except Exception as audit_error:
                logger.error(f"Audit log fallback failed: {audit_error}")
                return Decimal('0.00')
    
    def _get_current_liability(self, scope, sports=None, bet_types=None) -> List[Dict]:
        """Get current liability exposure"""
        # Mock implementation
        return [
            {
                'scope': scope,
                'identifier': 'Football',
                'current_liability': 150000.00,
                'limit': 200000.00,
                'exposure_percentage': 75.0
            }
        ]
    
    def _get_volatile_odds(self, start_time, end_time, volatility_threshold, change_frequency, sports=None, bet_types=None) -> List[Dict]:
        """Get volatile odds trong time period"""
        # Mock implementation
        import random
        if random.random() < 0.1:  # 10% chance of volatility
            return [
                {
                    'odds_id': 123,
                    'match_id': 456,
                    'sport': 'Football',
                    'changes': 6,
                    'max_change': 25.5
                }
            ]
        return []
    
    def _get_average_volume(self, start_time, end_time, window_minutes, sports=None, bet_types=None) -> Decimal:
        """Get average betting volume for historical comparison"""
        # Mock implementation - replace with actual historical data query
        cache_key = f"avg_volume_{start_time.isoformat()}_{end_time.isoformat()}_{window_minutes}"
        cached_avg = cache.get(cache_key)
        
        if cached_avg is not None:
            return Decimal(str(cached_avg))
        
        # Mock average calculation
        import random
        avg_volume = Decimal(str(random.uniform(8000, 30000)))
        cache.set(cache_key, float(avg_volume), self.cache_timeout)
        
        return avg_volume
    
    def _find_coordinated_bets(self, start_time, end_time, user_threshold, amount_similarity, sports=None, bet_types=None) -> List[Dict]:
        """Find coordinated betting patterns"""
        # Mock implementation - replace with actual betting pattern analysis
        import random
        if random.random() < 0.05:  # 5% chance of coordinated betting
            return [
                {
                    'group_id': 'coord_001',
                    'user_count': 12,
                    'total_amount': 45000.00,
                    'average_amount': 3750.00,
                    'sport': 'Football',
                    'bet_type': 'Moneyline'
                }
            ]
        return []
    
    def _get_late_heavy_bets(self, time_threshold, amount_threshold, user_threshold, sports=None, bet_types=None) -> List[Dict]:
        """Get late heavy betting patterns"""
        # Mock implementation - replace with actual late betting analysis
        import random
        if random.random() < 0.08:  # 8% chance of late heavy betting
            return [
                {
                    'bet_id': 'late_001',
                    'user_id': 'user_123',
                    'amount': 15000.00,
                    'time_before_event': 8,  # minutes
                    'sport': 'Basketball',
                    'bet_type': 'Point Spread'
                }
            ]
        return []
    
    def _find_arbitrage_attempts(self, start_time, end_time, profit_threshold, sports=None, bet_types=None) -> List[Dict]:
        """Find arbitrage betting attempts"""
        # Mock implementation - replace with actual arbitrage detection
        import random
        if random.random() < 0.03:  # 3% chance of arbitrage
            return [
                {
                    'attempt_id': 'arb_001',
                    'user_id': 'user_456',
                    'guaranteed_profit': 0.08,  # 8%
                    'total_stake': 20000.00,
                    'sport': 'Tennis',
                    'bet_type': 'Match Winner'
                }
            ]
        return []
    
    def _time_condition_met(self, current_time, trigger_condition) -> bool:
        """Check if time-based condition is met"""
        condition_type = trigger_condition.get('type')
        
        if condition_type == 'market_close':
            # Check if current time is near market close
            market_close_hour = trigger_condition.get('hour', 18)
            market_close_minute = trigger_condition.get('minute', 0)
            return current_time.hour == market_close_hour and current_time.minute >= market_close_minute - 30
        
        elif condition_type == 'peak_hours':
            # Check if current time is during peak betting hours
            start_hour = trigger_condition.get('start_hour', 19)
            end_hour = trigger_condition.get('end_hour', 23)
            return start_hour <= current_time.hour <= end_hour
        
        elif condition_type == 'weekend':
            # Check if current time is during weekend
            return current_time.weekday() >= 5  # Saturday = 5, Sunday = 6
        
        return False
    
    def _check_single_condition(self, condition) -> Dict[str, Any]:
        """Check a single condition for combination rules"""
        condition_type = condition.get('type')
        
        if condition_type == 'volume_spike':
            return self._check_volume_spike_condition(condition)
        elif condition_type == 'liability_threshold':
            return self._check_liability_threshold_condition(condition)
        elif condition_type == 'odds_volatility':
            return self._check_odds_volatility_condition(condition)
        
        return {'triggered': False, 'reason': f'Unknown condition type: {condition_type}'}
    
    def _check_volume_spike_condition(self, condition) -> Dict[str, Any]:
        """Check volume spike condition for combination rules"""
        # Simplified version for combination rules
        params = condition.get('parameters', {})
        spike_threshold = params.get('spike_threshold', 2.0)
        
        # Mock check
        import random
        if random.random() < 0.1:  # 10% chance
            return {'triggered': True, 'reason': 'Volume spike condition met'}
        
        return {'triggered': False, 'reason': 'Volume spike condition not met'}
    
    def _check_liability_threshold_condition(self, condition) -> Dict[str, Any]:
        """Check liability threshold condition for combination rules"""
        # Simplified version for combination rules
        params = condition.get('parameters', {})
        threshold = params.get('threshold', 80.0)
        
        # Mock check
        import random
        if random.random() < 0.15:  # 15% chance
            return {'triggered': True, 'reason': 'Liability threshold condition met'}
        
        return {'triggered': False, 'reason': 'Liability threshold condition not met'}
    
    def _check_odds_volatility_condition(self, condition) -> Dict[str, Any]:
        """Check odds volatility condition for combination rules"""
        # Simplified version for combination rules
        params = condition.get('parameters', {})
        volatility_threshold = params.get('volatility_threshold', 15.0)
        
        # Mock check
        import random
        if random.random() < 0.12:  # 12% chance
            return {'triggered': True, 'reason': 'Odds volatility condition met'}
        
        return {'triggered': False, 'reason': 'Odds volatility condition not met'}


class CircuitBreakerManager:
    """Manager để setup và quản lý circuit breaker rules"""
    
    def __init__(self):
        self.breaker = AdvancedCircuitBreaker()
    
    def create_default_rules(self):
        """Create default circuit breaker rules"""
        
        default_rules = [
            {
                'name': 'High Volume Spike Alert',
                'description': 'Detect unusual betting volume spikes',
                'trigger_type': 'VOLUME_SPIKE',
                'severity': 'MEDIUM',
                'action': 'ALERT',
                'rule_parameters': {
                    'spike_threshold': 3.0,
                    'time_window': 60,
                    'comparison_period': 7
                },
                'global_rule': True
            },
            {
                'name': 'Critical Liability Threshold',
                'description': 'Suspend trading when liability exceeds 90%',
                'trigger_type': 'LIABILITY_THRESHOLD',
                'severity': 'CRITICAL',
                'action': 'SUSPEND_SPORT',
                'rule_parameters': {
                    'threshold_percentage': 90.0,
                    'scope': 'sport'
                },
                'global_rule': True
            },
            {
                'name': 'Odds Manipulation Detection',
                'description': 'Detect rapid odds changes indicating manipulation',
                'trigger_type': 'ODDS_VOLATILITY',
                'severity': 'HIGH',
                'action': 'SUSPEND_MARKET',
                'rule_parameters': {
                    'volatility_threshold': 25.0,
                    'time_window': 10,
                    'change_frequency': 3
                },
                'global_rule': True
            },
            {
                'name': 'Coordinated Betting Alert',
                'description': 'Detect potential coordinated betting',
                'trigger_type': 'PATTERN_DETECTION',
                'severity': 'HIGH',
                'action': 'ALERT',
                'rule_parameters': {
                    'pattern_type': 'coordinated_betting',
                    'user_threshold': 15,
                    'time_window': 30,
                    'amount_similarity': 0.05
                },
                'global_rule': True
            }
        ]
        
        created_rules = []
        for rule_data in default_rules:
            rule, created = CircuitBreakerRule.objects.get_or_create(
                name=rule_data['name'],
                defaults=rule_data
            )
            if created:
                created_rules.append(rule)
                logger.info(f"Created circuit breaker rule: {rule.name}")
        
        return created_rules
    
    def run_monitoring_cycle(self):
        """Run one monitoring cycle - check all rules"""
        logger.info("Starting circuit breaker monitoring cycle")
        
        triggered_rules = self.breaker.check_all_rules()
        
        if triggered_rules:
            logger.warning(f"Circuit breaker monitoring: {len(triggered_rules)} rules triggered")
            for trigger in triggered_rules:
                logger.warning(f"  - {trigger['rule'].name}: {trigger['result']['reason']}")
        else:
            logger.info("Circuit breaker monitoring: No rules triggered")
        
        return triggered_rules


# Usage trong management command:
"""
# management/commands/run_circuit_breakers.py

from django.core.management.base import BaseCommand
import time
from risk_manager.circuit_breakers import CircuitBreakerManager

class Command(BaseCommand):
    help = 'Run circuit breaker monitoring'
    
    def add_arguments(self, parser):
        parser.add_argument('--interval', type=int, default=60, help='Check interval in seconds')
        parser.add_argument('--once', action='store_true', help='Run once and exit')
    
    def handle(self, *args, **options):
        manager = CircuitBreakerManager()
        interval = options['interval']
        
        if options['once']:
            manager.run_monitoring_cycle()
        else:
            while True:
                try:
                    manager.run_monitoring_cycle()
                    time.sleep(interval)
                except KeyboardInterrupt:
                    self.stdout.write("Stopping circuit breaker monitoring")
                    break
                except Exception as e:
                    self.stderr.write(f"Error in monitoring cycle: {e}")
                    time.sleep(interval)
"""
