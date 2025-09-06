"""
Test cases cho Circuit Breakers
"""

from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch, MagicMock
from decimal import Decimal

from .circuit_breakers import (
    CircuitBreakerRule, 
    CircuitBreakerEvent, 
    AdvancedCircuitBreaker,
    CircuitBreakerManager
)


class CircuitBreakerRuleTest(TestCase):
    """Test cho CircuitBreakerRule model"""
    
    def test_create_rule(self):
        """Test tạo circuit breaker rule"""
        rule = CircuitBreakerRule.objects.create(
            name='Test Volume Spike Rule',
            description='Test rule for volume spike detection',
            trigger_type='VOLUME_SPIKE',
            severity='MEDIUM',
            action='ALERT',
            rule_parameters={
                'spike_threshold': 2.5,
                'time_window': 30,
                'comparison_period': 3
            },
            global_rule=True
        )
        
        self.assertEqual(rule.name, 'Test Volume Spike Rule')
        self.assertEqual(rule.trigger_type, 'VOLUME_SPIKE')
        self.assertEqual(rule.severity, 'MEDIUM')
        self.assertEqual(rule.action, 'ALERT')
        self.assertTrue(rule.is_active)
        self.assertEqual(rule.triggered_count, 0)
    
    def test_rule_string_representation(self):
        """Test string representation của rule"""
        rule = CircuitBreakerRule.objects.create(
            name='Test Rule',
            description='Test description',
            trigger_type='LIABILITY_THRESHOLD',
            severity='HIGH',
            action='SUSPEND_SPORT'
        )
        
        expected = 'Test Rule (HIGH)'
        self.assertEqual(str(rule), expected)


class AdvancedCircuitBreakerTest(TestCase):
    """Test cho AdvancedCircuitBreaker class"""
    
    def setUp(self):
        """Setup test data"""
        self.breaker = AdvancedCircuitBreaker()
        
        # Tạo test rule
        self.rule = CircuitBreakerRule.objects.create(
            name='Test Rule',
            description='Test rule',
            trigger_type='VOLUME_SPIKE',
            severity='MEDIUM',
            action='ALERT',
            rule_parameters={
                'spike_threshold': 2.0,
                'time_window': 60,
                'comparison_period': 7
            }
        )
    
    @patch('risk_manager.circuit_breakers.AdvancedCircuitBreaker._get_betting_volume')
    @patch('risk_manager.circuit_breakers.AdvancedCircuitBreaker._get_average_volume')
    def test_check_volume_spike_triggered(self, mock_avg_volume, mock_current_volume):
        """Test volume spike detection khi triggered"""
        # Mock data
        mock_current_volume.return_value = Decimal('50000')
        mock_avg_volume.return_value = Decimal('20000')
        
        result = self.breaker._check_volume_spike(self.rule)
        
        self.assertTrue(result['triggered'])
        self.assertIn('Volume spike detected', result['reason'])
        self.assertIn('data', result)
        self.assertEqual(result['data']['spike_ratio'], 2.5)
    
    @patch('risk_manager.circuit_breakers.AdvancedCircuitBreaker._get_betting_volume')
    @patch('risk_manager.circuit_breakers.AdvancedCircuitBreaker._get_average_volume')
    def test_check_volume_spike_not_triggered(self, mock_avg_volume, mock_current_volume):
        """Test volume spike detection khi không triggered"""
        # Mock data
        mock_current_volume.return_value = Decimal('25000')
        mock_avg_volume.return_value = Decimal('20000')
        
        result = self.breaker._check_volume_spike(self.rule)
        
        self.assertFalse(result['triggered'])
        self.assertIn('Volume within normal range', result['reason'])
    
    def test_check_liability_threshold(self):
        """Test liability threshold check"""
        with patch.object(self.breaker, '_get_current_liability') as mock_liability:
            mock_liability.return_value = [
                {
                    'scope': 'sport',
                    'identifier': 'Football',
                    'current_liability': 180000.00,
                    'limit': 200000.00,
                    'exposure_percentage': 90.0
                }
            ]
            
            result = self.breaker._check_liability_threshold(self.rule)
            
            self.assertTrue(result['triggered'])
            self.assertIn('Liability threshold exceeded', result['reason'])
    
    def test_check_odds_volatility(self):
        """Test odds volatility check"""
        with patch.object(self.breaker, '_get_volatile_odds') as mock_volatile:
            mock_volatile.return_value = [
                {
                    'odds_id': 123,
                    'match_id': 456,
                    'sport': 'Football',
                    'changes': 6,
                    'max_change': 25.5
                }
            ]
            
            result = self.breaker._check_odds_volatility(self.rule)
            
            self.assertTrue(result['triggered'])
            self.assertIn('High odds volatility detected', result['reason'])
    
    def test_check_pattern_detection(self):
        """Test pattern detection"""
        # Test coordinated betting
        self.rule.rule_parameters = {
            'pattern_type': 'coordinated_betting',
            'user_threshold': 10,
            'time_window': 30,
            'amount_similarity': 0.1
        }
        
        with patch.object(self.breaker, '_find_coordinated_bets') as mock_coordinated:
            mock_coordinated.return_value = [
                {
                    'group_id': 'coord_001',
                    'user_count': 12,
                    'total_amount': 45000.00,
                    'average_amount': 3750.00,
                    'sport': 'Football',
                    'bet_type': 'Moneyline'
                }
            ]
            
            result = self.breaker._check_pattern_detection(self.rule)
            
            self.assertTrue(result['triggered'])
            self.assertIn('Coordinated betting detected', result['reason'])
    
    def test_time_condition_met(self):
        """Test time-based conditions"""
        current_time = timezone.now()
        
        # Test market close condition
        trigger_condition = {
            'type': 'market_close',
            'hour': current_time.hour,
            'minute': current_time.minute
        }
        
        result = self.breaker._time_condition_met(current_time, trigger_condition)
        self.assertTrue(result)
        
        # Test weekend condition
        weekend_trigger = {'type': 'weekend'}
        result = self.breaker._time_condition_met(current_time, weekend_trigger)
        # Result depends on current day of week


class CircuitBreakerManagerTest(TestCase):
    """Test cho CircuitBreakerManager class"""
    
    def setUp(self):
        """Setup test data"""
        self.manager = CircuitBreakerManager()
    
    def test_create_default_rules(self):
        """Test tạo default rules"""
        created_rules = self.manager.create_default_rules()
        
        self.assertGreater(len(created_rules), 0)
        
        # Kiểm tra các rule types
        rule_types = [rule.trigger_type for rule in created_rules]
        self.assertIn('VOLUME_SPIKE', rule_types)
        self.assertIn('LIABILITY_THRESHOLD', rule_types)
        self.assertIn('ODDS_VOLATILITY', rule_types)
        self.assertIn('PATTERN_DETECTION', rule_types)
    
    @patch('risk_manager.circuit_breakers.AdvancedCircuitBreaker.check_all_rules')
    def test_run_monitoring_cycle(self, mock_check_rules):
        """Test chạy monitoring cycle"""
        # Mock không có rules triggered
        mock_check_rules.return_value = []
        
        result = self.manager.run_monitoring_cycle()
        
        self.assertEqual(result, [])
        mock_check_rules.assert_called_once()
    
    @patch('risk_manager.circuit_breakers.AdvancedCircuitBreaker.check_all_rules')
    def test_run_monitoring_cycle_with_triggers(self, mock_check_rules):
        """Test monitoring cycle với rules triggered"""
        # Mock có rules triggered
        mock_rule = MagicMock()
        mock_rule.name = 'Test Rule'
        mock_rule.severity = 'HIGH'
        
        mock_check_rules.return_value = [
            {
                'rule': mock_rule,
                'result': {'triggered': True, 'reason': 'Test trigger'},
                'action_taken': {'action': 'ALERT', 'success': True}
            }
        ]
        
        result = self.manager.run_monitoring_cycle()
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['rule'].name, 'Test Rule')


class CircuitBreakerEventTest(TestCase):
    """Test cho CircuitBreakerEvent model"""
    
    def test_create_event(self):
        """Test tạo circuit breaker event"""
        rule = CircuitBreakerRule.objects.create(
            name='Test Rule',
            description='Test rule',
            trigger_type='VOLUME_SPIKE',
            severity='MEDIUM',
            action='ALERT'
        )
        
        event = CircuitBreakerEvent.objects.create(
            rule=rule,
            trigger_data={'test': 'data'},
            action_taken='ALERT'
        )
        
        self.assertEqual(event.rule, rule)
        self.assertEqual(event.action_taken, 'ALERT')
        self.assertIsNotNone(event.triggered_at)
        self.assertEqual(event.trigger_data, {'test': 'data'})


# Integration tests
class CircuitBreakerIntegrationTest(TestCase):
    """Integration tests cho toàn bộ circuit breaker system"""
    
    def setUp(self):
        """Setup integration test"""
        self.manager = CircuitBreakerManager()
        self.breaker = AdvancedCircuitBreaker()
    
    def test_full_circuit_breaker_workflow(self):
        """Test toàn bộ workflow của circuit breaker"""
        # 1. Tạo rules
        rules = self.manager.create_default_rules()
        self.assertGreater(len(rules), 0)
        
        # 2. Chạy monitoring cycle
        with patch.object(self.breaker, '_get_betting_volume') as mock_volume:
            with patch.object(self.breaker, '_get_average_volume') as mock_avg:
                # Mock volume spike
                mock_volume.return_value = Decimal('60000')
                mock_avg.return_value = Decimal('20000')
                
                # Chạy check
                result = self.breaker.check_all_rules()
                
                # Kết quả phụ thuộc vào mock data
                self.assertIsInstance(result, list)
    
    def test_circuit_breaker_with_real_models(self):
        """Test với real Django models"""
        # Tạo rule thực tế
        rule = CircuitBreakerRule.objects.create(
            name='Integration Test Rule',
            description='Rule for integration testing',
            trigger_type='VOLUME_SPIKE',
            severity='HIGH',
            action='ALERT',
            rule_parameters={
                'spike_threshold': 2.0,
                'time_window': 60,
                'comparison_period': 7
            }
        )
        
        # Kiểm tra rule được tạo
        self.assertIsNotNone(rule.id)
        self.assertTrue(rule.is_active)
        
        # Kiểm tra rule có thể được query
        active_rules = CircuitBreakerRule.objects.filter(is_active=True)
        self.assertIn(rule, active_rules)
