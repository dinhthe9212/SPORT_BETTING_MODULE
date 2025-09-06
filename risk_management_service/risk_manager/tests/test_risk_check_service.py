"""
Unit Tests cho RiskCheckService
Test các edge cases và error handling
"""

import pytest
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone
from unittest.mock import patch, MagicMock
from datetime import timedelta

from ..services import RiskCheckService
from ..models import RiskConfiguration, RiskAuditLog


class RiskCheckServiceTestCase(TestCase):
    """Test cases cho RiskCheckService"""
    
    def setUp(self):
        """Setup test data"""
        self.service = RiskCheckService()
        self.test_bet_data = {
            'user_id': 'test_user_123',
            'match_id': 'test_match_456',
            'bet_type_id': 'test_bet_type_789',
            'outcome': 'Home Win',
            'stake_amount': 100.00,
            'odds_value': 2.00
        }
        
        # Tạo test configuration
        self.risk_config = RiskConfiguration.objects.create(
            config_type='LIABILITY_THRESHOLD',
            config_key='match_liability_threshold',
            config_value={
                'match_id': 'test_match_456',
                'threshold': '5000.00'
            },
            description='Test liability threshold',
            updated_by='test_user'
        )
    
    def test_check_bet_risk_success(self):
        """Test successful risk check"""
        with patch.object(self.service, '_check_liability_threshold') as mock_liability, \
             patch.object(self.service, '_check_user_risk_limits') as mock_user, \
             patch.object(self.service, '_check_market_status') as mock_market:
            
            mock_liability.return_value = {'approved': True, 'liability_impact': 200.0}
            mock_user.return_value = {'approved': True, 'status': 'WITHIN_LIMITS'}
            mock_market.return_value = {'approved': True, 'status': 'MARKET_ACTIVE'}
            
            result = self.service.check_bet_risk(self.test_bet_data)
            
            self.assertTrue(result['approved'])
            self.assertEqual(result['risk_level'], 'VERY_LOW')
            self.assertIn('recommendations', result)
    
    def test_check_bet_risk_liability_exceeded(self):
        """Test risk check khi vượt ngưỡng liability"""
        with patch.object(self.service, '_check_liability_threshold') as mock_liability, \
             patch.object(self.service, '_check_user_risk_limits') as mock_user, \
             patch.object(self.service, '_check_market_status') as mock_market:
            
            mock_liability.return_value = {
                'approved': False, 
                'liability_impact': 200.0,
                'exceeds_by': 1000.0
            }
            mock_user.return_value = {'approved': True, 'status': 'WITHIN_LIMITS'}
            mock_market.return_value = {'approved': True, 'status': 'MARKET_ACTIVE'}
            
            result = self.service.check_bet_risk(self.test_bet_data)
            
            self.assertFalse(result['approved'])
            self.assertEqual(result['risk_level'], 'HIGH')
            self.assertIn('rejection_reason', result)
            self.assertIn('Vượt quá ngưỡng rủi ro', result['rejection_reason'])
    
    def test_check_bet_risk_user_limit_exceeded(self):
        """Test risk check khi user vượt giới hạn"""
        with patch.object(self.service, '_check_liability_threshold') as mock_liability, \
             patch.object(self.service, '_check_user_risk_limits') as mock_user, \
             patch.object(self.service, '_check_market_status') as mock_market:
            
            mock_liability.return_value = {'approved': True, 'liability_impact': 200.0}
            mock_user.return_value = {
                'approved': False, 
                'status': 'STAKE_EXCEEDS_LIMIT',
                'max_stake': 50.0
            }
            mock_market.return_value = {'approved': True, 'status': 'MARKET_ACTIVE'}
            
            result = self.service.check_bet_risk(self.test_bet_data)
            
            self.assertFalse(result['approved'])
            self.assertEqual(result['risk_level'], 'HIGH')
            self.assertIn('rejection_reason', result)
            self.assertIn('Vượt quá giới hạn cược tối đa', result['rejection_reason'])
    
    def test_check_bet_risk_market_suspended(self):
        """Test risk check khi thị trường bị tạm dừng"""
        with patch.object(self.service, '_check_liability_threshold') as mock_liability, \
             patch.object(self.service, '_check_user_risk_limits') as mock_user, \
             patch.object(self.service, '_check_market_status') as mock_market:
            
            mock_liability.return_value = {'approved': True, 'liability_impact': 200.0}
            mock_user.return_value = {'approved': True, 'status': 'WITHIN_LIMITS'}
            mock_market.return_value = {
                'approved': False, 
                'status': 'MARKET_SUSPENDED',
                'suspension_reason': 'RISK_MANAGEMENT'
            }
            
            result = self.service.check_bet_risk(self.test_bet_data)
            
            self.assertFalse(result['approved'])
            self.assertEqual(result['risk_level'], 'HIGH')
            self.assertIn('rejection_reason', result)
            self.assertIn('Thị trường đang tạm dừng giao dịch', result['rejection_reason'])
    
    def test_check_bet_risk_connection_error(self):
        """Test error handling cho connection errors"""
        with patch.object(self.service, '_check_liability_threshold') as mock_liability:
            mock_liability.side_effect = Exception("Connection timeout")
            
            result = self.service.check_bet_risk(self.test_bet_data)
            
            self.assertFalse(result['approved'])
            self.assertEqual(result['error'], 'Lỗi kết nối hệ thống, vui lòng thử lại sau')
            self.assertEqual(result['error_details']['error_category'], 'CONNECTION_ERROR')
            self.assertIn('recommendations', result)
    
    def test_check_bet_risk_validation_error(self):
        """Test error handling cho validation errors"""
        with patch.object(self.service, '_check_liability_threshold') as mock_liability:
            mock_liability.side_effect = ValueError("Invalid bet data")
            
            result = self.service.check_bet_risk(self.test_bet_data)
            
            self.assertFalse(result['approved'])
            self.assertEqual(result['error'], 'Dữ liệu đầu vào không hợp lệ')
            self.assertEqual(result['error_details']['error_category'], 'VALIDATION_ERROR')
    
    def test_check_bet_risk_database_error(self):
        """Test error handling cho database errors"""
        with patch.object(self.service, '_check_liability_threshold') as mock_liability:
            mock_liability.side_effect = Exception("Database connection failed")
            
            result = self.service.check_bet_risk(self.test_bet_data)
            
            self.assertFalse(result['approved'])
            self.assertEqual(result['error'], 'Lỗi truy vấn dữ liệu, vui lòng thử lại sau')
            self.assertEqual(result['error_details']['error_category'], 'DATABASE_ERROR')
    
    def test_liability_threshold_validation(self):
        """Test validation cho liability threshold configuration"""
        # Test với threshold hợp lệ
        result = self.service._check_liability_threshold(
            'test_match_456', 'test_bet_type_789', 'Home Win', Decimal('100.00')
        )
        self.assertTrue(result['approved'])
        
        # Test với threshold quá thấp (sẽ được điều chỉnh về minimum)
        with patch.object(self.service, '_calculate_current_liability') as mock_calc:
            mock_calc.return_value = Decimal('0.00')
            
            result = self.service._check_liability_threshold(
                'test_match_456', 'test_bet_type_789', 'Home Win', Decimal('100.00')
            )
            self.assertTrue(result['approved'])
    
    def test_risk_level_calculation(self):
        """Test tính toán risk level"""
        # Test HIGH risk level
        liability_check = {'approved': False}
        user_check = {'approved': True}
        market_check = {'approved': True}
        
        risk_level = self.service._calculate_risk_level(liability_check, user_check, market_check)
        self.assertEqual(risk_level, 'HIGH')
        
        # Test MEDIUM risk level
        liability_check = {
            'approved': True, 
            'remaining_capacity': 1000.0, 
            'threshold': 5000.0
        }
        risk_level = self.service._calculate_risk_level(liability_check, user_check, market_check)
        self.assertEqual(risk_level, 'MEDIUM')
        
        # Test LOW risk level
        liability_check = {
            'approved': True, 
            'remaining_capacity': 3000.0, 
            'threshold': 5000.0
        }
        risk_level = self.service._calculate_risk_level(liability_check, user_check, market_check)
        self.assertEqual(risk_level, 'LOW')
        
        # Test VERY_LOW risk level
        liability_check = {
            'approved': True, 
            'remaining_capacity': 4000.0, 
            'threshold': 5000.0
        }
        risk_level = self.service._calculate_risk_level(liability_check, user_check, market_check)
        self.assertEqual(risk_level, 'VERY_LOW')
    
    def test_recommendations_generation(self):
        """Test tạo recommendations"""
        # Test recommendations cho liability exceeded
        liability_check = {'approved': False}
        user_check = {'approved': True}
        market_check = {'approved': True}
        
        recommendations = self.service._generate_recommendations(
            liability_check, user_check, market_check
        )
        
        self.assertIn("Giảm số tiền cược để giảm rủi ro", recommendations)
        self.assertIn("Chọn outcome khác có rủi ro thấp hơn", recommendations)
        
        # Test recommendations cho user limit exceeded
        liability_check = {'approved': True}
        user_check = {
            'approved': False, 
            'status': 'STAKE_EXCEEDS_LIMIT',
            'max_stake': 50.0
        }
        market_check = {'approved': True}
        
        recommendations = self.service._generate_recommendations(
            liability_check, user_check, market_check
        )
        
        self.assertIn("Giảm số tiền cược xuống dưới $50.0", recommendations)
    
    def test_audit_logging(self):
        """Test audit logging"""
        bet_data = self.test_bet_data.copy()
        result = {'approved': True, 'risk_level': 'LOW'}
        
        # Test tạo audit log
        self.service._log_risk_check_audit(bet_data, result)
        
        # Verify audit log được tạo
        audit_log = RiskAuditLog.objects.filter(
            action_type='RISK_CHECK',
            related_object_type='BET'
        ).first()
        
        self.assertIsNotNone(audit_log)
        self.assertEqual(audit_log.description, f"Risk check for bet: {bet_data['user_id']} - {bet_data['match_id']}")
        self.assertEqual(audit_log.action_details['risk_result'], result)


class RiskCheckServiceIntegrationTestCase(TestCase):
    """Integration tests cho RiskCheckService với real database"""
    
    def setUp(self):
        """Setup integration test data"""
        self.service = RiskCheckService()
        
        # Tạo comprehensive test data
        self.create_test_data()
    
    def create_test_data(self):
        """Tạo test data cho integration tests"""
        # Tạo multiple risk configurations
        RiskConfiguration.objects.bulk_create([
            RiskConfiguration(
                config_type='LIABILITY_THRESHOLD',
                config_key='match_liability_threshold',
                config_value={'match_id': 'match_1', 'threshold': '1000.00'},
                description='Low threshold test',
                updated_by='test_user'
            ),
            RiskConfiguration(
                config_type='LIABILITY_THRESHOLD',
                config_key='match_liability_threshold',
                config_value={'match_id': 'match_2', 'threshold': '10000.00'},
                description='High threshold test',
                updated_by='test_user'
            ),
            RiskConfiguration(
                config_type='USER_RISK_LIMITS',
                config_key='user_risk_limits',
                config_value={
                    'user_id': 'user_1',
                    'max_stake': '500.00',
                    'daily_limit': '2000.00'
                },
                description='User limits test',
                updated_by='test_user'
            )
        ])
    
    def test_multiple_configurations(self):
        """Test xử lý multiple configurations"""
        configs = RiskConfiguration.objects.filter(
            config_type='LIABILITY_THRESHOLD'
        )
        
        self.assertEqual(configs.count(), 2)
        
        # Test tìm configuration cụ thể
        match_1_config = configs.filter(
            config_value__match_id='match_1'
        ).first()
        
        self.assertIsNotNone(match_1_config)
        self.assertEqual(match_1_config.config_value['threshold'], '1000.00')
    
    def test_configuration_validation_edge_cases(self):
        """Test validation cho edge cases"""
        # Test với invalid threshold value
        invalid_config = RiskConfiguration.objects.create(
            config_type='LIABILITY_THRESHOLD',
            config_key='invalid_threshold_test',
            config_value={'match_id': 'match_3', 'threshold': 'invalid_value'},
            description='Invalid threshold test',
            updated_by='test_user'
        )
        
        # Test xử lý invalid threshold
        with patch.object(self.service, '_calculate_current_liability') as mock_calc:
            mock_calc.return_value = Decimal('0.00')
            
            result = self.service._check_liability_threshold(
                'match_3', 'bet_type_1', 'Home Win', Decimal('100.00')
            )
            
            # Should fallback to default threshold
            self.assertTrue(result['approved'])
            self.assertEqual(result['threshold'], 10000.00)  # Default value
    
    def test_performance_with_large_dataset(self):
        """Test performance với large dataset"""
        # Tạo large number of configurations
        large_configs = []
        for i in range(100):
            large_configs.append(
                RiskConfiguration(
                    config_type='LIABILITY_THRESHOLD',
                    config_key=f'performance_test_{i}',
                    config_value={'match_id': f'match_{i}', 'threshold': '5000.00'},
                    description=f'Performance test {i}',
                    updated_by='test_user'
                )
            )
        
        RiskConfiguration.objects.bulk_create(large_configs)
        
        # Test query performance
        start_time = timezone.now()
        
        configs = RiskConfiguration.objects.filter(
            config_type='LIABILITY_THRESHOLD'
        ).select_related()
        
        query_time = (timezone.now() - start_time).total_seconds()
        
        # Query should complete within reasonable time
        self.assertLess(query_time, 1.0)  # Less than 1 second
        self.assertEqual(configs.count(), 102)  # 2 original + 100 new


if __name__ == '__main__':
    pytest.main([__file__])
