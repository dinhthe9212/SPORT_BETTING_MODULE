import logging
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
from django.utils import timezone
from django.db.models import Avg, Sum, Count, Max, F
from django.conf import settings
from django.core.cache import cache
import requests

from .models import (
    PriceVolatilityMonitor, MarketActivityMonitor, TradingSuspension,
    RiskConfiguration, RiskAlert, RiskAuditLog,
    SportRiskConfiguration, BetTypeRiskConfiguration, LiveRiskMonitor,
    OddsVolatilityLog, LiabilityExposure, BettingPatternAnalysis,
    SPORT_NAMES, SPORT_CATEGORIES, BET_TYPE_CATEGORIES
)
from .external_imports import get_sports_data_match, get_betting_models

logger = logging.getLogger('risk_manager')

class PriceVolatilityService:
    """Service quản lý biến động giá"""
    
    def __init__(self):
        self.volatility_thresholds = self._load_volatility_thresholds()
    
    def _load_volatility_thresholds(self) -> Dict:
        """Load ngưỡng biến động từ configuration"""
        try:
            config = RiskConfiguration.objects.get(
                config_key='price_volatility_thresholds',
                is_active=True
            )
            return config.config_value
        except RiskConfiguration.DoesNotExist:
            # Default thresholds
            return {
                'low_threshold': 5.0,      # 5%
                'medium_threshold': 10.0,   # 10%
                'high_threshold': 20.0,     # 20%
                'critical_threshold': 30.0  # 30%
            }
    
    def monitor_price_change(self, bet_slip_id: str, market_identifier: str,
                           original_price: Decimal, current_price: Decimal) -> Optional[PriceVolatilityMonitor]:
        """Theo dõi thay đổi giá và tạo cảnh báo nếu cần"""
        
        # Tính toán % thay đổi giá
        if original_price <= 0:
            logger.warning(f"Invalid original price for bet slip {bet_slip_id}")
            return None
        
        price_change = ((current_price - original_price) / original_price) * 100
        volatility_score = abs(price_change)
        
        # Xác định mức độ nghiêm trọng
        severity = self._determine_severity(volatility_score)
        
        # Tạo monitor record
        monitor = PriceVolatilityMonitor.objects.create(
            bet_slip_id=bet_slip_id,
            market_identifier=market_identifier,
            original_price=original_price,
            current_price=current_price,
            price_change_percentage=price_change,
            volatility_score=volatility_score,
            severity_level=severity,
            metadata={
                'detection_timestamp': timezone.now().isoformat(),
                'thresholds_used': self.volatility_thresholds
            }
        )
        
        # Tạo alert nếu cần thiết
        if severity in ['HIGH', 'CRITICAL']:
            self._create_volatility_alert(monitor)
        
        # Log audit
        self._log_audit_action(
            action_type='VOLATILITY_DETECTED',
            description=f"Price volatility detected for {bet_slip_id}: {price_change:.2f}%",
            related_object_type='PriceVolatilityMonitor',
            related_object_id=str(monitor.id),
            action_details={
                'bet_slip_id': bet_slip_id,
                'price_change': float(price_change),
                'severity': severity
            }
        )
        
        logger.info(f"Price volatility monitored: {bet_slip_id} - {price_change:.2f}% ({severity})")
        return monitor
    
    def _determine_severity(self, volatility_score: Decimal) -> str:
        """Xác định mức độ nghiêm trọng"""
        if volatility_score >= self.volatility_thresholds['critical_threshold']:
            return 'CRITICAL'
        elif volatility_score >= self.volatility_thresholds['high_threshold']:
            return 'HIGH'
        elif volatility_score >= self.volatility_thresholds['medium_threshold']:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _create_volatility_alert(self, monitor: PriceVolatilityMonitor):
        """Tạo cảnh báo biến động giá"""
        alert = RiskAlert.objects.create(
            alert_type='PRICE_VOLATILITY',
            severity=monitor.severity_level,
            title=f"High Price Volatility Detected",
            message=f"Price volatility of {monitor.price_change_percentage:.2f}% detected for bet slip {monitor.bet_slip_id}",
            related_data={
                'monitor_id': str(monitor.id),
                'bet_slip_id': monitor.bet_slip_id,
                'market_identifier': monitor.market_identifier,
                'price_change': float(monitor.price_change_percentage),
                'original_price': float(monitor.original_price),
                'current_price': float(monitor.current_price)
            }
        )
        
        logger.warning(f"Volatility alert created: {alert.id}")
    
    def get_volatility_stats(self, hours: int = 24) -> Dict:
        """Lấy thống kê biến động giá trong khoảng thời gian"""
        since = timezone.now() - timedelta(hours=hours)
        
        monitors = PriceVolatilityMonitor.objects.filter(
            detection_time__gte=since
        )
        
        stats = monitors.aggregate(
            total_detections=Count('id'),
            avg_volatility=Avg('volatility_score'),
            max_volatility=Max('volatility_score')
        )
        
        severity_counts = monitors.values('severity_level').annotate(
            count=Count('id')
        )
        
        return {
            'period_hours': hours,
            'total_detections': stats['total_detections'] or 0,
            'average_volatility': float(stats['avg_volatility'] or 0),
            'max_volatility': float(stats['max_volatility'] or 0),
            'severity_breakdown': {item['severity_level']: item['count'] for item in severity_counts}
        }
    
    def _log_audit_action(self, action_type: str, description: str, 
                         related_object_type: str = None, related_object_id: str = None,
                         action_details: Dict = None):
        """Log audit action"""
        RiskAuditLog.objects.create(
            action_type=action_type,
            action_description=description,
            user_id='system',  # System-generated action
            ip_address='127.0.0.1',
            related_object_type=related_object_type,
            related_object_id=related_object_id,
            action_details=action_details or {}
        )

class MarketActivityService:
    """Service theo dõi hoạt động thị trường"""
    
    def __init__(self):
        self.activity_thresholds = self._load_activity_thresholds()
    
    def _load_activity_thresholds(self) -> Dict:
        """Load ngưỡng hoạt động từ configuration"""
        try:
            config = RiskConfiguration.objects.get(
                config_key='market_activity_thresholds',
                is_active=True
            )
            return config.config_value
        except RiskConfiguration.DoesNotExist:
            return {
                'unusual_volume_multiplier': 3.0,  # 3x volume bình thường
                'rapid_price_change_seconds': 60,   # Thay đổi giá trong 60 giây
                'high_frequency_orders_per_minute': 10,
                'large_order_threshold': 10000.0,
                'suspicious_pattern_confidence': 0.8
            }
    
    def detect_unusual_volume(self, market_identifier: str, current_volume: Decimal,
                            historical_average: Decimal) -> Optional[MarketActivityMonitor]:
        """Phát hiện volume bất thường"""
        
        if historical_average <= 0:
            return None
        
        volume_ratio = current_volume / historical_average
        threshold = self.activity_thresholds['unusual_volume_multiplier']
        
        if volume_ratio >= threshold:
            severity = 'HIGH' if volume_ratio >= threshold * 1.5 else 'MEDIUM'
            confidence = min(volume_ratio / threshold, 1.0)
            
            monitor = MarketActivityMonitor.objects.create(
                activity_type='UNUSUAL_VOLUME',
                market_identifier=market_identifier,
                user_id='system',
                description=f"Unusual volume detected: {volume_ratio:.2f}x normal volume",
                severity_level=severity,
                confidence_score=confidence,
                volume_data={
                    'current_volume': float(current_volume),
                    'historical_average': float(historical_average),
                    'volume_ratio': float(volume_ratio),
                    'threshold': threshold
                }
            )
            
            logger.warning(f"Unusual volume detected: {market_identifier} - {volume_ratio:.2f}x")
            return monitor
        
        return None
    
    def detect_rapid_price_changes(self, market_identifier: str, price_changes: List[Dict]) -> Optional[MarketActivityMonitor]:
        """Phát hiện thay đổi giá nhanh"""
        
        rapid_changes = []
        threshold_seconds = self.activity_thresholds['rapid_price_change_seconds']
        
        for i in range(1, len(price_changes)):
            time_diff = (price_changes[i]['timestamp'] - price_changes[i-1]['timestamp']).total_seconds()
            
            if time_diff <= threshold_seconds:
                price_change = abs(price_changes[i]['price'] - price_changes[i-1]['price'])
                rapid_changes.append({
                    'time_diff': time_diff,
                    'price_change': price_change,
                    'from_price': price_changes[i-1]['price'],
                    'to_price': price_changes[i]['price']
                })
        
        if rapid_changes:
            # Tính confidence dựa trên số lượng và mức độ thay đổi
            confidence = min(len(rapid_changes) / 5.0, 1.0)  # Max confidence at 5 rapid changes
            severity = 'HIGH' if len(rapid_changes) >= 3 else 'MEDIUM'
            
            monitor = MarketActivityMonitor.objects.create(
                activity_type='RAPID_PRICE_CHANGE',
                market_identifier=market_identifier,
                user_id='system',
                description=f"Rapid price changes detected: {len(rapid_changes)} changes within {threshold_seconds}s",
                severity_level=severity,
                confidence_score=confidence,
                price_data={
                    'rapid_changes': rapid_changes,
                    'total_changes': len(rapid_changes),
                    'threshold_seconds': threshold_seconds
                }
            )
            
            logger.warning(f"Rapid price changes detected: {market_identifier} - {len(rapid_changes)} changes")
            return monitor
        
        return None
    
    def detect_high_frequency_trading(self, user_id: str, market_identifier: str,
                                    recent_orders: List[Dict]) -> Optional[MarketActivityMonitor]:
        """Phát hiện giao dịch tần số cao"""
        
        threshold = self.activity_thresholds['high_frequency_orders_per_minute']
        
        # Đếm orders trong 1 phút gần nhất
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        recent_count = len([
            order for order in recent_orders
            if order['timestamp'] >= one_minute_ago
        ])
        
        if recent_count >= threshold:
            severity = 'HIGH' if recent_count >= threshold * 2 else 'MEDIUM'
            confidence = min(recent_count / threshold, 1.0)
            
            monitor = MarketActivityMonitor.objects.create(
                activity_type='HIGH_FREQUENCY_TRADING',
                market_identifier=market_identifier,
                user_id=user_id,
                description=f"High frequency trading detected: {recent_count} orders in 1 minute",
                severity_level=severity,
                confidence_score=confidence,
                related_orders=[order['id'] for order in recent_orders[-10:]],  # Last 10 orders
                volume_data={
                    'orders_per_minute': recent_count,
                    'threshold': threshold,
                    'total_recent_orders': len(recent_orders)
                }
            )
            
            logger.warning(f"High frequency trading detected: {user_id} - {recent_count} orders/min")
            return monitor
        
        return None
    
    def detect_large_orders(self, user_id: str, market_identifier: str,
                          order_amount: Decimal) -> Optional[MarketActivityMonitor]:
        """Phát hiện lệnh lớn"""
        
        threshold = self.activity_thresholds['large_order_threshold']
        
        if order_amount >= threshold:
            severity = 'HIGH' if order_amount >= threshold * 2 else 'MEDIUM'
            confidence = min(order_amount / threshold / 2, 1.0)
            
            monitor = MarketActivityMonitor.objects.create(
                activity_type='LARGE_ORDER',
                market_identifier=market_identifier,
                user_id=user_id,
                description=f"Large order detected: {order_amount}",
                severity_level=severity,
                confidence_score=confidence,
                volume_data={
                    'order_amount': float(order_amount),
                    'threshold': threshold
                }
            )
            
            logger.warning(f"Large order detected: {user_id} - {order_amount}")
            return monitor
        
        return None

class TradingSuspensionService:
    """Service quản lý tạm dừng giao dịch"""
    
    def suspend_trading(self, suspension_type: str, reason: str, description: str,
                       suspended_by: str, sport_id: str = None, market_identifier: str = None,
                       user_id: str = None, event_id: str = None,
                       expires_at: datetime = None) -> TradingSuspension:
        """Tạm dừng giao dịch"""
        
        suspension = TradingSuspension.objects.create(
            suspension_type=suspension_type,
            reason=reason,
            description=description,
            sport_id=sport_id,
            market_identifier=market_identifier,
            user_id=user_id,
            event_id=event_id,
            suspended_by=suspended_by,
            expires_at=expires_at,
            metadata={
                'created_at': timezone.now().isoformat(),
                'auto_expire': expires_at is not None
            }
        )
        
        # Tạo alert
        alert = RiskAlert.objects.create(
            alert_type='TRADING_SUSPENSION',
            severity='HIGH',
            title=f"Trading Suspended - {suspension_type}",
            message=f"Trading suspended: {description}",
            related_data={
                'suspension_id': str(suspension.id),
                'suspension_type': suspension_type,
                'reason': reason,
                'sport_id': sport_id,
                'market_identifier': market_identifier,
                'user_id': user_id,
                'event_id': event_id
            }
        )
        
        # Log audit
        RiskAuditLog.objects.create(
            action_type='SUSPENSION_CREATED',
            action_description=f"Trading suspension created: {suspension_type} - {reason}",
            user_id=suspended_by,
            ip_address='127.0.0.1',
            related_object_type='TradingSuspension',
            related_object_id=str(suspension.id),
            action_details={
                'suspension_type': suspension_type,
                'reason': reason,
                'description': description
            }
        )
        
        logger.warning(f"Trading suspended: {suspension_type} - {reason}")
        return suspension
    
    def lift_suspension(self, suspension_id: str, lifted_by: str) -> bool:
        """Dỡ bỏ tạm dừng giao dịch"""
        
        try:
            suspension = TradingSuspension.objects.get(id=suspension_id, status='ACTIVE')
            suspension.lift_suspension(lifted_by)
            
            # Log audit
            RiskAuditLog.objects.create(
                action_type='SUSPENSION_LIFTED',
                action_description=f"Trading suspension lifted: {suspension.suspension_type}",
                user_id=lifted_by,
                ip_address='127.0.0.1',
                related_object_type='TradingSuspension',
                related_object_id=str(suspension.id),
                action_details={
                    'original_reason': suspension.reason,
                    'duration_minutes': (timezone.now() - suspension.suspended_at).total_seconds() / 60
                }
            )
            
            logger.info(f"Trading suspension lifted: {suspension_id}")
            return True
            
        except TradingSuspension.DoesNotExist:
            logger.error(f"Suspension not found or already lifted: {suspension_id}")
            return False
    
    def check_trading_allowed(self, user_id: str = None, sport_id: str = None,
                            market_identifier: str = None, event_id: str = None) -> Tuple[bool, str]:
        """Kiểm tra xem giao dịch có được phép không"""
        
        # Kiểm tra global suspension
        global_suspensions = TradingSuspension.objects.filter(
            suspension_type='GLOBAL',
            status='ACTIVE'
        )
        if global_suspensions.exists():
            return False, "Global trading suspension is active"
        
        # Kiểm tra user-specific suspension
        if user_id:
            user_suspensions = TradingSuspension.objects.filter(
                suspension_type='USER_SPECIFIC',
                user_id=user_id,
                status='ACTIVE'
            )
            if user_suspensions.exists():
                return False, f"User {user_id} is suspended from trading"
        
        # Kiểm tra sport-specific suspension
        if sport_id:
            sport_suspensions = TradingSuspension.objects.filter(
                suspension_type='SPORT_SPECIFIC',
                sport_id=sport_id,
                status='ACTIVE'
            )
            if sport_suspensions.exists():
                return False, f"Trading suspended for sport {sport_id}"
        
        # Kiểm tra market-specific suspension
        if market_identifier:
            market_suspensions = TradingSuspension.objects.filter(
                suspension_type='MARKET_SPECIFIC',
                market_identifier=market_identifier,
                status='ACTIVE'
            )
            if market_suspensions.exists():
                return False, f"Trading suspended for market {market_identifier}"
        
        # Kiểm tra event-specific suspension
        if event_id:
            event_suspensions = TradingSuspension.objects.filter(
                suspension_type='EVENT_SPECIFIC',
                event_id=event_id,
                status='ACTIVE'
            )
            if event_suspensions.exists():
                return False, f"Trading suspended for event {event_id}"
        
        return True, "Trading allowed"
    
    def get_active_suspensions(self) -> List[Dict]:
        """Lấy danh sách tạm dừng đang hoạt động"""
        
        suspensions = TradingSuspension.objects.filter(status='ACTIVE').order_by('-suspended_at')
        
        return [{
            'id': str(suspension.id),
            'suspension_type': suspension.suspension_type,
            'reason': suspension.reason,
            'description': suspension.description,
            'sport_id': suspension.sport_id,
            'market_identifier': suspension.market_identifier,
            'user_id': suspension.user_id,
            'event_id': suspension.event_id,
            'suspended_at': suspension.suspended_at.isoformat(),
            'suspended_by': suspension.suspended_by,
            'expires_at': suspension.expires_at.isoformat() if suspension.expires_at else None
        } for suspension in suspensions]

class RiskDashboardService:
    """Service cung cấp dữ liệu cho Risk Dashboard"""
    
    def get_dashboard_summary(self, hours: int = 24) -> Dict:
        """Lấy tổng quan dashboard"""
        
        since = timezone.now() - timedelta(hours=hours)
        
        # Alert statistics
        alerts = RiskAlert.objects.filter(created_at__gte=since)
        alert_stats = {
            'total_alerts': alerts.count(),
            'active_alerts': alerts.filter(status='ACTIVE').count(),
            'high_severity_alerts': alerts.filter(severity__in=['HIGH', 'CRITICAL']).count(),
            'alerts_by_type': dict(alerts.values('alert_type').annotate(count=Count('id')).values_list('alert_type', 'count'))
        }
        
        # Suspension statistics
        suspensions = TradingSuspension.objects.filter(suspended_at__gte=since)
        suspension_stats = {
            'total_suspensions': suspensions.count(),
            'active_suspensions': suspensions.filter(status='ACTIVE').count(),
            'suspensions_by_type': dict(suspensions.values('suspension_type').annotate(count=Count('id')).values_list('suspension_type', 'count'))
        }
        
        # Market activity statistics
        activities = MarketActivityMonitor.objects.filter(detected_at__gte=since)
        activity_stats = {
            'total_activities': activities.count(),
            'high_severity_activities': activities.filter(severity_level__in=['HIGH', 'CRITICAL']).count(),
            'activities_by_type': dict(activities.values('activity_type').annotate(count=Count('id')).values_list('activity_type', 'count'))
        }
        
        # Price volatility statistics
        volatility_service = PriceVolatilityService()
        volatility_stats = volatility_service.get_volatility_stats(hours)
        
        return {
            'period_hours': hours,
            'timestamp': timezone.now().isoformat(),
            'alerts': alert_stats,
            'suspensions': suspension_stats,
            'market_activities': activity_stats,
            'price_volatility': volatility_stats
        }
    
    def get_recent_activities(self, limit: int = 50) -> List[Dict]:
        """Lấy hoạt động gần đây"""
        
        activities = []
        
        # Recent alerts
        recent_alerts = RiskAlert.objects.order_by('-created_at')[:limit//2]
        for alert in recent_alerts:
            activities.append({
                'type': 'alert',
                'timestamp': alert.created_at.isoformat(),
                'severity': alert.severity,
                'title': alert.title,
                'message': alert.message,
                'status': alert.status,
                'id': str(alert.id)
            })
        
        # Recent suspensions
        recent_suspensions = TradingSuspension.objects.order_by('-suspended_at')[:limit//2]
        for suspension in recent_suspensions:
            activities.append({
                'type': 'suspension',
                'timestamp': suspension.suspended_at.isoformat(),
                'severity': 'HIGH',
                'title': f"Trading Suspended - {suspension.suspension_type}",
                'message': suspension.description,
                'status': suspension.status,
                'id': str(suspension.id)
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return activities[:limit]

# ============================================================================
# BETTING SYSTEM SPECIFIC RISK SERVICES
# ============================================================================

class BettingRiskConfigurationService:
    """Service quản lý risk configuration cho betting system"""
    
    def __init__(self):
        self.betting_service_url = self._get_betting_service_url()
        self.sports_data_service_url = self._get_sports_data_service_url()
    
    def _get_betting_service_url(self) -> str:
        """Lấy URL của betting service"""
        return "http://localhost:8002"  # Default, should be from config
    
    def _get_sports_data_service_url(self) -> str:
        """Lấy URL của sports data service"""
        return "http://localhost:8005"  # Default, should be from config
    
    def initialize_sport_risk_configurations(self) -> Dict[str, Any]:
        """Khởi tạo risk configuration cho tất cả 50+ sports"""
        try:
            # Lấy danh sách sports từ betting service
            sports_response = requests.get(f"{self.betting_service_url}/api/sports/")
            sports_data = sports_response.json()
            sports = sports_data.get('results', [])
            
            created_configs = []
            updated_configs = []
            
            for sport in sports:
                sport_id = sport['id']
                sport_name = sport['name']
                sport_category = sport.get('category', 'SPECIAL')
                
                # Xác định risk level dựa trên sport category
                risk_level = self._determine_sport_risk_level(sport_category, sport_name)
                
                # Lấy hoặc tạo sport risk configuration
                config, created = SportRiskConfiguration.objects.get_or_create(
                    sport_id=sport_id,
                    sport_name=sport_name,
                    defaults={
                        'sport_category': sport_category,
                        'risk_level': risk_level,
                        'max_daily_volume': self._get_max_daily_volume(sport_category),
                        'max_single_bet': self._get_max_single_bet(sport_category),
                        'max_odds_value': self._get_max_odds_value(sport_category),
                        'min_odds_value': Decimal('1.01'),
                        'max_odds_change_percent': self._get_max_odds_change_percent(sport_category),
                        'volatility_threshold': self._get_volatility_threshold(sport_category),
                        'auto_suspend_enabled': True,
                        'suspension_threshold': Decimal('75.00'),
                        'max_liability_per_match': self._get_max_liability_per_match(sport_category),
                        'max_liability_per_outcome': self._get_max_liability_per_outcome(sport_category),
                        'updated_by': 'system_init'
                    }
                )
                
                if created:
                    created_configs.append(config)
                else:
                    # Cập nhật thông tin nếu cần
                    if config.sport_category != sport_category:
                        config.sport_category = sport_category
                        config.risk_level = risk_level
                        config.updated_by = 'system_update'
                        config.save()
                        updated_configs.append(config)
            
            logger.info(f"Sport risk configurations initialized: {len(created_configs)} created, {len(updated_configs)} updated")
            
            return {
                'status': 'success',
                'created_count': len(created_configs),
                'updated_count': len(updated_configs),
                'total_sports': len(sports),
                'created_configs': [{'id': str(c.id), 'sport_name': c.sport_name, 'risk_level': c.risk_level} for c in created_configs],
                'updated_configs': [{'id': str(c.id), 'sport_name': c.sport_name, 'risk_level': c.risk_level} for c in updated_configs]
            }
            
        except Exception as e:
            logger.error(f"Error initializing sport risk configurations: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def initialize_bet_type_risk_configurations(self) -> Dict[str, Any]:
        """Khởi tạo risk configuration cho tất cả 50+ bet types"""
        try:
            # Lấy danh sách bet types từ betting service
            bet_types_response = requests.get(f"{self.betting_service_url}/api/bet-types/")
            bet_types_data = bet_types_response.json()
            bet_types = bet_types_data.get('results', [])
            
            created_configs = []
            updated_configs = []
            
            for bet_type in bet_types:
                bet_type_id = bet_type['id']
                bet_type_name = bet_type['name']
                bet_type_category = bet_type.get('category', 'SPECIAL_MARKETS')
                sport_name = bet_type['sport']['name']
                
                # Xác định risk level dựa trên bet type category
                risk_level = self._determine_bet_type_risk_level(bet_type_category, bet_type_name)
                
                # Lấy hoặc tạo bet type risk configuration
                config, created = BetTypeRiskConfiguration.objects.get_or_create(
                    bet_type_id=bet_type_id,
                    bet_type_name=bet_type_name,
                    sport_name=sport_name,
                    defaults={
                        'bet_type_category': bet_type_category,
                        'risk_level': risk_level,
                        'max_stake_multiplier': self._get_max_stake_multiplier(bet_type_category),
                        'max_odds_multiplier': self._get_max_odds_multiplier(bet_type_category),
                        'max_liability_per_bet': self._get_max_liability_per_bet(bet_type_category),
                        'max_total_liability': self._get_max_total_liability(bet_type_category),
                        'auto_adjust_enabled': True,
                        'adjustment_trigger_percent': Decimal('80.00'),
                        'adjustment_step': self._get_adjustment_step(bet_type_category),
                        'updated_by': 'system_init'
                    }
                )
                
                if created:
                    created_configs.append(config)
                else:
                    # Cập nhật thông tin nếu cần
                    if config.bet_type_category != bet_type_category:
                        config.bet_type_category = bet_type_category
                        config.risk_level = risk_level
                        config.updated_by = 'system_update'
                        config.save()
                        updated_configs.append(config)
            
            logger.info(f"Bet type risk configurations initialized: {len(created_configs)} created, {len(updated_configs)} updated")
            
            return {
                'status': 'success',
                'created_count': len(created_configs),
                'updated_count': len(updated_configs),
                'total_bet_types': len(bet_types),
                'created_configs': [{'id': str(c.id), 'bet_type_name': c.bet_type_name, 'sport_name': c.sport_name, 'risk_level': c.risk_level} for c in created_configs],
                'updated_configs': [{'id': str(c.id), 'bet_type_name': c.bet_type_name, 'sport_name': c.sport_name, 'risk_level': c.risk_level} for c in updated_configs]
            }
            
        except Exception as e:
            logger.error(f"Error initializing bet type risk configurations: {e}")
            return {'status': 'error', 'message': str(e)}
    
    def _determine_sport_risk_level(self, category: str, sport_name: str) -> str:
        """Xác định risk level cho sport dựa trên category"""
        high_risk_sports = ['MMA', 'Boxing', 'Esports', 'Special Markets']
        medium_risk_categories = ['RACING', 'MOTOR', 'SPECIAL']
        
        if sport_name in high_risk_sports:
            return 'HIGH'
        elif category in medium_risk_categories:
            return 'MEDIUM'
        elif category in ['BALL_SPORTS', 'INDIVIDUAL']:
            return 'LOW'
        else:
            return 'MEDIUM'
    
    def _determine_bet_type_risk_level(self, category: str, bet_type_name: str) -> str:
        """Xác định risk level cho bet type dựa trên category"""
        high_risk_bet_types = ['Correct Score', 'Method of Victory', 'Frame Handicap', 'Highest Break']
        critical_risk_categories = ['SPECIAL_MARKETS', 'COMBINATIONS']
        
        if bet_type_name in high_risk_bet_types:
            return 'HIGH'
        elif category in critical_risk_categories:
            return 'HIGH'
        elif category in ['FUTURES', 'SPECIAL_EVENTS']:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_max_daily_volume(self, category: str) -> Decimal:
        """Lấy max daily volume theo sport category"""
        volumes = {
            'BALL_SPORTS': Decimal('1000000.00'),
            'RACING': Decimal('500000.00'),
            'COMBAT': Decimal('300000.00'),
            'INDIVIDUAL': Decimal('200000.00'),
            'WINTER': Decimal('150000.00'),
            'WATER': Decimal('100000.00'),
            'MOTOR': Decimal('400000.00'),
            'SPECIAL': Decimal('100000.00'),
        }
        return volumes.get(category, Decimal('200000.00'))
    
    def _get_max_single_bet(self, category: str) -> Decimal:
        """Lấy max single bet theo sport category"""
        amounts = {
            'BALL_SPORTS': Decimal('50000.00'),
            'RACING': Decimal('25000.00'),
            'COMBAT': Decimal('15000.00'),
            'INDIVIDUAL': Decimal('10000.00'),
            'WINTER': Decimal('8000.00'),
            'WATER': Decimal('5000.00'),
            'MOTOR': Decimal('20000.00'),
            'SPECIAL': Decimal('5000.00'),
        }
        return amounts.get(category, Decimal('10000.00'))
    
    def _get_max_odds_value(self, category: str) -> Decimal:
        """Lấy max odds value theo sport category"""
        odds = {
            'BALL_SPORTS': Decimal('500.00'),
            'RACING': Decimal('1000.00'),
            'COMBAT': Decimal('200.00'),
            'INDIVIDUAL': Decimal('100.00'),
            'WINTER': Decimal('300.00'),
            'WATER': Decimal('150.00'),
            'MOTOR': Decimal('800.00'),
            'SPECIAL': Decimal('2000.00'),
        }
        return odds.get(category, Decimal('500.00'))
    
    def _get_max_odds_change_percent(self, category: str) -> Decimal:
        """Lấy max odds change percent theo sport category"""
        percentages = {
            'BALL_SPORTS': Decimal('25.00'),
            'RACING': Decimal('75.00'),
            'COMBAT': Decimal('50.00'),
            'INDIVIDUAL': Decimal('30.00'),
            'WINTER': Decimal('40.00'),
            'WATER': Decimal('35.00'),
            'MOTOR': Decimal('60.00'),
            'SPECIAL': Decimal('100.00'),
        }
        return percentages.get(category, Decimal('50.00'))
    
    def _get_volatility_threshold(self, category: str) -> Decimal:
        """Lấy volatility threshold theo sport category"""
        thresholds = {
            'BALL_SPORTS': Decimal('15.00'),
            'RACING': Decimal('40.00'),
            'COMBAT': Decimal('30.00'),
            'INDIVIDUAL': Decimal('20.00'),
            'WINTER': Decimal('25.00'),
            'WATER': Decimal('20.00'),
            'MOTOR': Decimal('35.00'),
            'SPECIAL': Decimal('50.00'),
        }
        return thresholds.get(category, Decimal('25.00'))
    
    def _get_max_liability_per_match(self, category: str) -> Decimal:
        """Lấy max liability per match theo sport category"""
        liabilities = {
            'BALL_SPORTS': Decimal('2000000.00'),
            'RACING': Decimal('1000000.00'),
            'COMBAT': Decimal('600000.00'),
            'INDIVIDUAL': Decimal('400000.00'),
            'WINTER': Decimal('300000.00'),
            'WATER': Decimal('200000.00'),
            'MOTOR': Decimal('800000.00'),
            'SPECIAL': Decimal('200000.00'),
        }
        return liabilities.get(category, Decimal('500000.00'))
    
    def _get_max_liability_per_outcome(self, category: str) -> Decimal:
        """Lấy max liability per outcome theo sport category"""
        liabilities = {
            'BALL_SPORTS': Decimal('500000.00'),
            'RACING': Decimal('300000.00'),
            'COMBAT': Decimal('200000.00'),
            'INDIVIDUAL': Decimal('150000.00'),
            'WINTER': Decimal('100000.00'),
            'WATER': Decimal('80000.00'),
            'MOTOR': Decimal('250000.00'),
            'SPECIAL': Decimal('100000.00'),
        }
        return liabilities.get(category, Decimal('200000.00'))
    
    def _get_max_stake_multiplier(self, category: str) -> Decimal:
        """Lấy max stake multiplier theo bet type category"""
        multipliers = {
            'MATCH_RESULT': Decimal('2.00'),
            'SCORING': Decimal('1.50'),
            'PERFORMANCE': Decimal('1.20'),
            'SPECIAL_EVENTS': Decimal('0.80'),
            'COMBINATIONS': Decimal('0.50'),
            'FUTURES': Decimal('1.00'),
            'LIVE_BETTING': Decimal('1.80'),
            'SPECIAL_MARKETS': Decimal('0.30'),
        }
        return multipliers.get(category, Decimal('1.00'))
    
    def _get_max_odds_multiplier(self, category: str) -> Decimal:
        """Lấy max odds multiplier theo bet type category"""
        multipliers = {
            'MATCH_RESULT': Decimal('1.50'),
            'SCORING': Decimal('2.00'),
            'PERFORMANCE': Decimal('1.80'),
            'SPECIAL_EVENTS': Decimal('3.00'),
            'COMBINATIONS': Decimal('5.00'),
            'FUTURES': Decimal('2.50'),
            'LIVE_BETTING': Decimal('1.20'),
            'SPECIAL_MARKETS': Decimal('10.00'),
        }
        return multipliers.get(category, Decimal('2.00'))
    
    def _get_max_liability_per_bet(self, category: str) -> Decimal:
        """Lấy max liability per bet theo bet type category"""
        liabilities = {
            'MATCH_RESULT': Decimal('100000.00'),
            'SCORING': Decimal('50000.00'),
            'PERFORMANCE': Decimal('30000.00'),
            'SPECIAL_EVENTS': Decimal('20000.00'),
            'COMBINATIONS': Decimal('10000.00'),
            'FUTURES': Decimal('40000.00'),
            'LIVE_BETTING': Decimal('80000.00'),
            'SPECIAL_MARKETS': Decimal('5000.00'),
        }
        return liabilities.get(category, Decimal('30000.00'))
    
    def _get_max_total_liability(self, category: str) -> Decimal:
        """Lấy max total liability theo bet type category"""
        liabilities = {
            'MATCH_RESULT': Decimal('2000000.00'),
            'SCORING': Decimal('1000000.00'),
            'PERFORMANCE': Decimal('600000.00'),
            'SPECIAL_EVENTS': Decimal('400000.00'),
            'COMBINATIONS': Decimal('200000.00'),
            'FUTURES': Decimal('800000.00'),
            'LIVE_BETTING': Decimal('1500000.00'),
            'SPECIAL_MARKETS': Decimal('100000.00'),
        }
        return liabilities.get(category, Decimal('500000.00'))
    
    def _get_adjustment_step(self, category: str) -> Decimal:
        """Lấy adjustment step theo bet type category"""
        steps = {
            'MATCH_RESULT': Decimal('0.02'),
            'SCORING': Decimal('0.05'),
            'PERFORMANCE': Decimal('0.03'),
            'SPECIAL_EVENTS': Decimal('0.10'),
            'COMBINATIONS': Decimal('0.15'),
            'FUTURES': Decimal('0.08'),
            'LIVE_BETTING': Decimal('0.01'),
            'SPECIAL_MARKETS': Decimal('0.20'),
        }
        return steps.get(category, Decimal('0.05'))
    
    def get_sport_risk_config(self, sport_id: int) -> Optional[SportRiskConfiguration]:
        """Lấy risk configuration cho sport"""
        try:
            return SportRiskConfiguration.objects.get(sport_id=sport_id, is_active=True)
        except SportRiskConfiguration.DoesNotExist:
            logger.warning(f"Sport risk configuration not found for sport_id: {sport_id}")
            return None
    
    def get_bet_type_risk_config(self, bet_type_id: int, sport_name: str) -> Optional[BetTypeRiskConfiguration]:
        """Lấy risk configuration cho bet type"""
        try:
            return BetTypeRiskConfiguration.objects.get(
                bet_type_id=bet_type_id,
                sport_name=sport_name,
                is_active=True
            )
        except BetTypeRiskConfiguration.DoesNotExist:
            logger.warning(f"Bet type risk configuration not found for bet_type_id: {bet_type_id}, sport: {sport_name}")
            return None
    
    def suspend_sport_trading(self, sport_id: int, reason: str, suspended_by: str) -> bool:
        """Tạm dừng trading cho sport"""
        try:
            config = self.get_sport_risk_config(sport_id)
            if config:
                config.suspend_trading(reason, suspended_by)
                logger.warning(f"Sport trading suspended: {config.sport_name} - {reason}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error suspending sport trading: {e}")
            return False
    
    def resume_sport_trading(self, sport_id: int, resumed_by: str) -> bool:
        """Khôi phục trading cho sport"""
        try:
            config = self.get_sport_risk_config(sport_id)
            if config:
                config.resume_trading(resumed_by)
                logger.info(f"Sport trading resumed: {config.sport_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error resuming sport trading: {e}")
            return False

class BettingRiskMonitorService:
    """Service monitor rủi ro real-time cho betting system"""
    
    def __init__(self):
        self.config_service = BettingRiskConfigurationService()
    
    def monitor_match_volume(self, match_id: int, sport_name: str, current_volume: Decimal) -> Optional[LiveRiskMonitor]:
        """Monitor volume cược cho match"""
        try:
            # Lấy sport risk config
            sport_response = requests.get(f"{self.config_service.betting_service_url}/api/sports/?name={sport_name}")
            if sport_response.status_code != 200:
                return None
            
            sports_data = sport_response.json()
            if not sports_data.get('results'):
                return None
            
            sport_id = sports_data['results'][0]['id']
            sport_config = self.config_service.get_sport_risk_config(sport_id)
            
            if not sport_config:
                return None
            
            # Kiểm tra có vượt ngưỡng không
            daily_limit = sport_config.max_daily_volume
            volume_percentage = (current_volume / daily_limit) * 100 if daily_limit > 0 else 0
            
            if volume_percentage >= 75:  # 75% threshold
                monitor = LiveRiskMonitor.objects.create(
                    monitor_type='MATCH_VOLUME',
                    match_id=match_id,
                    sport_name=sport_name,
                    current_value=current_volume,
                    threshold_value=daily_limit,
                    risk_score=min(volume_percentage, 100),
                    confidence_level=Decimal('0.95'),
                    detection_details={
                        'volume_percentage': float(volume_percentage),
                        'sport_config_id': str(sport_config.id),
                        'daily_limit': float(daily_limit)
                    }
                )
                
                if volume_percentage >= 90:
                    monitor.trigger_alert({
                        'alert_reason': 'Volume approaching daily limit',
                        'action_required': 'Consider suspending new bets'
                    })
                
                logger.warning(f"Match volume monitor triggered: {match_id} - {volume_percentage:.1f}%")
                return monitor
            
            return None
            
        except Exception as e:
            logger.error(f"Error monitoring match volume: {e}")
            return None
    
    def monitor_odds_movement(self, odds_id: int, match_id: int, bet_type_id: int, 
                            sport_name: str, old_value: Decimal, new_value: Decimal) -> Optional[OddsVolatilityLog]:
        """Monitor biến động odds"""
        try:
            # Tính % thay đổi
            if old_value <= 0:
                return None
            
            change_percentage = ((new_value - old_value) / old_value) * 100
            volatility_score = abs(change_percentage)
            
            # Lấy sport config để kiểm tra threshold
            sport_response = requests.get(f"{self.config_service.betting_service_url}/api/sports/?name={sport_name}")
            if sport_response.status_code == 200:
                sports_data = sport_response.json()
                if sports_data.get('results'):
                    sport_id = sports_data['results'][0]['id']
                    sport_config = self.config_service.get_sport_risk_config(sport_id)
                    
                    if sport_config and volatility_score > sport_config.volatility_threshold:
                        # Xác định risk impact
                        if volatility_score >= sport_config.max_odds_change_percent:
                            risk_impact = 'CRITICAL'
                        elif volatility_score >= sport_config.volatility_threshold * 2:
                            risk_impact = 'HIGH'
                        elif volatility_score >= sport_config.volatility_threshold:
                            risk_impact = 'MEDIUM'
                        else:
                            risk_impact = 'LOW'
                        
                        # Log volatility
                        volatility_log = OddsVolatilityLog.objects.create(
                            odds_id=odds_id,
                            match_id=match_id,
                            bet_type_id=bet_type_id,
                            sport_name=sport_name,
                            outcome='Unknown',  # Should be passed as parameter
                            old_value=old_value,
                            new_value=new_value,
                            change_percentage=change_percentage,
                            change_reason='SYSTEM_AUTO',
                            volatility_score=volatility_score,
                            risk_impact=risk_impact,
                            adjusted_by='system',
                            metadata={
                                'sport_config_id': str(sport_config.id),
                                'threshold_exceeded': True,
                                'volatility_threshold': float(sport_config.volatility_threshold)
                            }
                        )
                        
                        logger.warning(f"Odds volatility detected: {sport_name} - {change_percentage:.2f}%")
                        return volatility_log
            
            return None
            
        except Exception as e:
            logger.error(f"Error monitoring odds movement: {e}")
            return None
    
    def monitor_liability_exposure(self, match_id: int, sport_name: str, bet_type_id: int, 
                                 outcome: str, current_stake: Decimal, potential_payout: Decimal) -> Optional[LiabilityExposure]:
        """Monitor liability exposure"""
        try:
            net_exposure = potential_payout - current_stake
            
            # Lấy bet type config để kiểm tra limits
            bet_type_response = requests.get(f"{self.config_service.betting_service_url}/api/bet-types/{bet_type_id}/")
            if bet_type_response.status_code != 200:
                return None
            
            bet_type_data = bet_type_response.json()
            bet_type_config = self.config_service.get_bet_type_risk_config(bet_type_id, sport_name)
            
            if not bet_type_config:
                return None
            
            # Tính exposure percentage
            exposure_limit = bet_type_config.max_total_liability
            exposure_percentage = (net_exposure / exposure_limit) * 100 if exposure_limit > 0 else 0
            
            # Cập nhật hoặc tạo liability exposure record
            exposure, created = LiabilityExposure.objects.update_or_create(
                match_id=match_id,
                bet_type_id=bet_type_id,
                outcome=outcome,
                defaults={
                    'sport_name': sport_name,
                    'current_stake': current_stake,
                    'potential_payout': potential_payout,
                    'net_exposure': net_exposure,
                    'exposure_percentage': exposure_percentage,
                    'exposure_limit': exposure_limit,
                    'auto_adjust_threshold': bet_type_config.adjustment_trigger_percent,
                    'last_bet_time': timezone.now(),
                    'bets_count': 1 if created else F('bets_count') + 1,
                    'calculation_metadata': {
                        'bet_type_config_id': str(bet_type_config.id),
                        'calculation_time': timezone.now().isoformat()
                    }
                }
            )
            
            # Cập nhật risk rating
            exposure.update_risk_rating()
            
            # Kiểm tra có cần auto adjust không
            if exposure_percentage >= bet_type_config.adjustment_trigger_percent:
                exposure.trigger_auto_adjust()
                
                logger.warning(f"Liability exposure threshold exceeded: {sport_name} {outcome} - {exposure_percentage:.1f}%")
            
            return exposure
            
        except Exception as e:
            logger.error(f"Error monitoring liability exposure: {e}")
            return None
    
    def analyze_betting_patterns(self, user_ids: List[str], match_ids: List[int], 
                               time_window_minutes: int = 60) -> Optional[BettingPatternAnalysis]:
        """Phân tích betting patterns để phát hiện bất thường"""
        try:
            # Lấy dữ liệu betting từ betting service trong time window
            since = timezone.now() - timedelta(minutes=time_window_minutes)
            
            # Phân tích coordinated betting
            if len(user_ids) >= 3 and len(set(match_ids)) <= 2:
                # Có thể là coordinated betting
                confidence_score = min(len(user_ids) / 10.0, 1.0)
                severity = 'HIGH' if len(user_ids) >= 5 else 'MEDIUM'
                
                analysis = BettingPatternAnalysis.objects.create(
                    pattern_type='COORDINATED_BETTING',
                    severity_level=severity,
                    confidence_score=Decimal(str(confidence_score)),
                    match_ids=match_ids,
                    sport_names=self._get_sport_names_for_matches(match_ids),
                    user_ids=user_ids,
                    pattern_description=f"Coordinated betting detected: {len(user_ids)} users betting on {len(set(match_ids))} matches",
                    detection_criteria={
                        'min_users': 3,
                        'max_matches': 2,
                        'time_window_minutes': time_window_minutes
                    },
                    supporting_evidence={
                        'user_count': len(user_ids),
                        'unique_matches': len(set(match_ids)),
                        'detection_time': timezone.now().isoformat()
                    },
                    pattern_start_time=since,
                    pattern_end_time=timezone.now()
                )
                
                logger.warning(f"Coordinated betting pattern detected: {len(user_ids)} users")
                return analysis
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing betting patterns: {e}")
            return None
    
    def _get_sport_names_for_matches(self, match_ids: List[int]) -> List[str]:
        """Lấy sport names cho các matches"""
        try:
            sport_names = []
            for match_id in match_ids:
                match_response = requests.get(f"{self.config_service.betting_service_url}/api/matches/{match_id}/")
                if match_response.status_code == 200:
                    match_data = match_response.json()
                    sport_name = match_data.get('sport', {}).get('name')
                    if sport_name and sport_name not in sport_names:
                        sport_names.append(sport_name)
            return sport_names
        except Exception as e:
            logger.error(f"Error getting sport names for matches: {e}")
            return []

class BettingRiskReportingService:
    """Service báo cáo rủi ro cho betting system"""
    
    def __init__(self):
        self.config_service = BettingRiskConfigurationService()
        self.monitor_service = BettingRiskMonitorService()
    
    def generate_daily_risk_report(self, date: datetime = None) -> Dict[str, Any]:
        """Tạo báo cáo rủi ro hàng ngày"""
        if not date:
            date = timezone.now().date()
        
        start_date = timezone.make_aware(datetime.combine(date, datetime.min.time()))
        end_date = start_date + timedelta(days=1)
        
        try:
            # Sports risk summary
            sports_summary = self._get_sports_risk_summary(start_date, end_date)
            
            # Bet types risk summary
            bet_types_summary = self._get_bet_types_risk_summary(start_date, end_date)
            
            # Live monitoring summary
            monitoring_summary = self._get_monitoring_summary(start_date, end_date)
            
            # Odds volatility summary
            volatility_summary = self._get_volatility_summary(start_date, end_date)
            
            # Liability exposure summary
            liability_summary = self._get_liability_summary(start_date, end_date)
            
            # Pattern analysis summary
            pattern_summary = self._get_pattern_analysis_summary(start_date, end_date)
            
            report = {
                'report_date': date.isoformat(),
                'generated_at': timezone.now().isoformat(),
                'period': {
                    'start': start_date.isoformat(),
                    'end': end_date.isoformat()
                },
                'sports_risk': sports_summary,
                'bet_types_risk': bet_types_summary,
                'live_monitoring': monitoring_summary,
                'odds_volatility': volatility_summary,
                'liability_exposure': liability_summary,
                'pattern_analysis': pattern_summary,
                'overall_risk_score': self._calculate_overall_risk_score(
                    sports_summary, bet_types_summary, monitoring_summary, 
                    volatility_summary, liability_summary, pattern_summary
                )
            }
            
            logger.info(f"Daily risk report generated for {date}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating daily risk report: {e}")
            return {'error': str(e), 'report_date': date.isoformat()}
    
    def _get_sports_risk_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Lấy summary rủi ro cho sports"""
        sports_configs = SportRiskConfiguration.objects.filter(is_active=True)
        
        total_sports = sports_configs.count()
        suspended_sports = sports_configs.filter(is_trading_suspended=True).count()
        high_risk_sports = sports_configs.filter(risk_level__in=['HIGH', 'CRITICAL']).count()
        
        # Group by category
        category_stats = {}
        for category, _ in SPORT_CATEGORIES:
            category_sports = sports_configs.filter(sport_category=category)
            category_stats[category] = {
                'total': category_sports.count(),
                'suspended': category_sports.filter(is_trading_suspended=True).count(),
                'high_risk': category_sports.filter(risk_level__in=['HIGH', 'CRITICAL']).count()
            }
        
        return {
            'total_sports': total_sports,
            'suspended_sports': suspended_sports,
            'high_risk_sports': high_risk_sports,
            'suspension_rate': (suspended_sports / total_sports * 100) if total_sports > 0 else 0,
            'high_risk_rate': (high_risk_sports / total_sports * 100) if total_sports > 0 else 0,
            'category_breakdown': category_stats
        }
    
    def _get_bet_types_risk_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Lấy summary rủi ro cho bet types"""
        bet_type_configs = BetTypeRiskConfiguration.objects.filter(is_active=True)
        
        total_bet_types = bet_type_configs.count()
        suspended_bet_types = bet_type_configs.filter(is_suspended=True).count()
        high_risk_bet_types = bet_type_configs.filter(risk_level__in=['HIGH', 'CRITICAL']).count()
        
        # Group by category
        category_stats = {}
        for category, _ in BET_TYPE_CATEGORIES:
            category_bet_types = bet_type_configs.filter(bet_type_category=category)
            category_stats[category] = {
                'total': category_bet_types.count(),
                'suspended': category_bet_types.filter(is_suspended=True).count(),
                'high_risk': category_bet_types.filter(risk_level__in=['HIGH', 'CRITICAL']).count()
            }
        
        return {
            'total_bet_types': total_bet_types,
            'suspended_bet_types': suspended_bet_types,
            'high_risk_bet_types': high_risk_bet_types,
            'suspension_rate': (suspended_bet_types / total_bet_types * 100) if total_bet_types > 0 else 0,
            'high_risk_rate': (high_risk_bet_types / total_bet_types * 100) if total_bet_types > 0 else 0,
            'category_breakdown': category_stats
        }
    
    def _get_monitoring_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Lấy summary live monitoring"""
        monitors = LiveRiskMonitor.objects.filter(
            first_detected__gte=start_date,
            first_detected__lt=end_date
        )
        
        total_monitors = monitors.count()
        triggered_monitors = monitors.filter(status='TRIGGERED').count()
        resolved_monitors = monitors.filter(status='RESOLVED').count()
        
        # Group by type
        type_stats = {}
        for monitor_type, _ in LiveRiskMonitor.MONITOR_TYPES:
            type_monitors = monitors.filter(monitor_type=monitor_type)
            type_stats[monitor_type] = {
                'total': type_monitors.count(),
                'triggered': type_monitors.filter(status='TRIGGERED').count(),
                'resolved': type_monitors.filter(status='RESOLVED').count()
            }
        
        return {
            'total_monitors': total_monitors,
            'triggered_monitors': triggered_monitors,
            'resolved_monitors': resolved_monitors,
            'trigger_rate': (triggered_monitors / total_monitors * 100) if total_monitors > 0 else 0,
            'resolution_rate': (resolved_monitors / triggered_monitors * 100) if triggered_monitors > 0 else 0,
            'type_breakdown': type_stats
        }
    
    def _get_volatility_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Lấy summary odds volatility"""
        volatility_logs = OddsVolatilityLog.objects.filter(
            timestamp__gte=start_date,
            timestamp__lt=end_date
        )
        
        total_changes = volatility_logs.count()
        high_impact_changes = volatility_logs.filter(risk_impact__in=['HIGH', 'CRITICAL']).count()
        
        # Average volatility by sport
        sport_volatility = {}
        for sport_name in SPORT_NAMES:
            sport_logs = volatility_logs.filter(sport_name=sport_name)
            if sport_logs.exists():
                avg_volatility = sport_logs.aggregate(avg=Avg('volatility_score'))['avg']
                sport_volatility[sport_name] = float(avg_volatility) if avg_volatility else 0
        
        return {
            'total_odds_changes': total_changes,
            'high_impact_changes': high_impact_changes,
            'high_impact_rate': (high_impact_changes / total_changes * 100) if total_changes > 0 else 0,
            'sport_volatility': sport_volatility
        }
    
    def _get_liability_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Lấy summary liability exposure"""
        exposures = LiabilityExposure.objects.filter(
            calculated_at__gte=start_date,
            calculated_at__lt=end_date
        )
        
        total_exposures = exposures.count()
        critical_exposures = exposures.filter(risk_rating='CRITICAL').count()
        auto_adjustments = exposures.filter(auto_adjust_triggered=True).count()
        
        # Total exposure by sport
        sport_exposure = {}
        for sport_name in SPORT_NAMES:
            sport_exposures = exposures.filter(sport_name=sport_name)
            if sport_exposures.exists():
                total_exposure = sport_exposures.aggregate(total=Sum('net_exposure'))['total']
                sport_exposure[sport_name] = float(total_exposure) if total_exposure else 0
        
        return {
            'total_exposures': total_exposures,
            'critical_exposures': critical_exposures,
            'auto_adjustments': auto_adjustments,
            'critical_rate': (critical_exposures / total_exposures * 100) if total_exposures > 0 else 0,
            'auto_adjustment_rate': (auto_adjustments / total_exposures * 100) if total_exposures > 0 else 0,
            'sport_exposure': sport_exposure
        }
    
    def _get_pattern_analysis_summary(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Lấy summary pattern analysis"""
        patterns = BettingPatternAnalysis.objects.filter(
            detected_at__gte=start_date,
            detected_at__lt=end_date
        )
        
        total_patterns = patterns.count()
        confirmed_patterns = patterns.filter(investigation_status='CONFIRMED').count()
        false_positives = patterns.filter(investigation_status='FALSE_POSITIVE').count()
        
        # Group by pattern type
        type_stats = {}
        for pattern_type, _ in BettingPatternAnalysis.PATTERN_TYPES:
            type_patterns = patterns.filter(pattern_type=pattern_type)
            type_stats[pattern_type] = {
                'total': type_patterns.count(),
                'confirmed': type_patterns.filter(investigation_status='CONFIRMED').count(),
                'false_positive': type_patterns.filter(investigation_status='FALSE_POSITIVE').count()
            }
        
        return {
            'total_patterns': total_patterns,
            'confirmed_patterns': confirmed_patterns,
            'false_positives': false_positives,
            'confirmation_rate': (confirmed_patterns / total_patterns * 100) if total_patterns > 0 else 0,
            'false_positive_rate': (false_positives / total_patterns * 100) if total_patterns > 0 else 0,
            'type_breakdown': type_stats
        }
    
    def _calculate_overall_risk_score(self, sports_summary: Dict, bet_types_summary: Dict,
                                    monitoring_summary: Dict, volatility_summary: Dict,
                                    liability_summary: Dict, pattern_summary: Dict) -> float:
        """Tính overall risk score (0-100)"""
        # Weighted scoring
        weights = {
            'sports_risk': 0.15,
            'bet_types_risk': 0.15,
            'monitoring_risk': 0.20,
            'volatility_risk': 0.20,
            'liability_risk': 0.20,
            'pattern_risk': 0.10
        }
        
        scores = {
            'sports_risk': sports_summary.get('suspension_rate', 0) + sports_summary.get('high_risk_rate', 0),
            'bet_types_risk': bet_types_summary.get('suspension_rate', 0) + bet_types_summary.get('high_risk_rate', 0),
            'monitoring_risk': monitoring_summary.get('trigger_rate', 0),
            'volatility_risk': volatility_summary.get('high_impact_rate', 0),
            'liability_risk': liability_summary.get('critical_rate', 0),
            'pattern_risk': pattern_summary.get('confirmation_rate', 0)
        }
        
        overall_score = sum(scores[key] * weights[key] for key in scores.keys())
        return min(overall_score, 100.0)


class RiskCheckService:
    """Service kiểm tra rủi ro cho betting operations"""
    
    def __init__(self):
        self.logger = logging.getLogger('risk_manager')
    
    def check_bet_risk(self, bet_data: Dict) -> Dict:
        """Kiểm tra rủi ro của một bet"""
        try:
            user_id = bet_data['user_id']
            match_id = bet_data['match_id']
            bet_type_id = bet_data['bet_type_id']
            outcome = bet_data['outcome']
            stake_amount = Decimal(str(bet_data['stake_amount']))
            odds_value = Decimal(str(bet_data['odds_value']))
            
            # Tính toán potential payout
            potential_payout = stake_amount * odds_value
            
            # Kiểm tra ngưỡng rủi ro
            risk_check = self._check_liability_threshold(
                match_id, bet_type_id, outcome, potential_payout
            )
            
            # Kiểm tra user risk limits
            user_risk_check = self._check_user_risk_limits(user_id, stake_amount)
            
            # Kiểm tra market status
            market_status_check = self._check_market_status(match_id)
            
            # Tổng hợp kết quả
            approved = all([
                risk_check['approved'],
                user_risk_check['approved'],
                market_status_check['approved']
            ])
            
            result = {
                'approved': approved,
                'risk_level': self._calculate_risk_level(risk_check, user_risk_check, market_status_check),
                'liability_impact': risk_check['liability_impact'],
                'user_risk_status': user_risk_check['status'],
                'market_status': market_status_check['status'],
                'recommendations': self._generate_recommendations(risk_check, user_risk_check, market_status_check)
            }
            
            if not approved:
                result['rejection_reason'] = self._get_rejection_reason(risk_check, user_risk_check, market_status_check)
            
            # Log audit
            self._log_risk_check_audit(bet_data, result)
            
            return result
            
        except Exception as e:
            error_type = type(e).__name__
            error_message = str(e)
            
            # Phân loại lỗi cụ thể
            if 'connection' in error_message.lower() or 'timeout' in error_message.lower():
                error_category = 'CONNECTION_ERROR'
                user_message = 'Lỗi kết nối hệ thống, vui lòng thử lại sau'
            elif 'validation' in error_message.lower() or 'invalid' in error_message.lower():
                error_category = 'VALIDATION_ERROR'
                user_message = 'Dữ liệu đầu vào không hợp lệ'
            elif 'database' in error_message.lower() or 'query' in error_message.lower():
                error_category = 'DATABASE_ERROR'
                user_message = 'Lỗi truy vấn dữ liệu, vui lòng thử lại sau'
            elif 'permission' in error_message.lower() or 'access' in error_message.lower():
                error_category = 'PERMISSION_ERROR'
                user_message = 'Không có quyền truy cập tính năng này'
            else:
                error_category = 'SYSTEM_ERROR'
                user_message = 'Lỗi hệ thống, vui lòng liên hệ hỗ trợ'
            
            self.logger.error(f"Error in check_bet_risk: {error_type} - {error_message}")
            
            return {
                'approved': False,
                'error': user_message,
                'error_details': {
                    'error_type': error_type,
                    'error_category': error_category,
                    'error_message': error_message,
                    'timestamp': timezone.now().isoformat()
                },
                'risk_level': 'UNKNOWN',
                'recommendations': [
                    'Kiểm tra lại thông tin đầu vào',
                    'Thử lại sau vài phút',
                    'Liên hệ hỗ trợ nếu lỗi tiếp tục xảy ra'
                ]
            }
    
    def _check_liability_threshold(self, match_id: str, bet_type_id: str, 
                                  outcome: str, potential_payout: Decimal) -> Dict:
        """Kiểm tra ngưỡng rủi ro cho liability"""
        try:
            # Lấy cấu hình rủi ro cho match
            risk_config = RiskConfiguration.objects.filter(
                config_key='match_liability_threshold',
                config_value__match_id=match_id,
                is_active=True
            ).first()
            
            if not risk_config:
                # Sử dụng ngưỡng mặc định
                threshold = Decimal('10000.00')  # $10,000 mặc định
            else:
                # Validate configuration values
                config_value = risk_config.config_value
                raw_threshold = config_value.get('threshold', '10000.00')
                
                try:
                    threshold = Decimal(str(raw_threshold))
                    
                    # Validation rules
                    min_threshold = Decimal('100.00')  # Tối thiểu $100
                    max_threshold = Decimal('1000000.00')  # Tối đa $1,000,000
                    
                    if threshold < min_threshold:
                        self.logger.warning(f"Threshold {threshold} below minimum {min_threshold}, using minimum")
                        threshold = min_threshold
                    elif threshold > max_threshold:
                        self.logger.warning(f"Threshold {threshold} above maximum {max_threshold}, using maximum")
                        threshold = max_threshold
                        
                except (ValueError, TypeError, Decimal.InvalidOperation) as validation_error:
                    self.logger.error(f"Invalid threshold value '{raw_threshold}': {validation_error}")
                    threshold = Decimal('10000.00')  # Fallback to default
            
            # Tính toán liability hiện tại
            current_liability = self._calculate_current_liability(match_id, bet_type_id, outcome)
            
            # Tính toán liability mới nếu bet được chấp nhận
            new_liability = current_liability + potential_payout
            
            # Kiểm tra ngưỡng
            if new_liability > threshold:
                return {
                    'approved': False,
                    'liability_impact': float(potential_payout),
                    'current_liability': float(current_liability),
                    'new_liability': float(new_liability),
                    'threshold': float(threshold),
                    'exceeds_by': float(new_liability - threshold)
                }
            else:
                return {
                    'approved': True,
                    'liability_impact': float(potential_payout),
                    'current_liability': float(current_liability),
                    'new_liability': float(new_liability),
                    'threshold': float(threshold),
                    'remaining_capacity': float(threshold - new_liability)
                }
                
        except Exception as e:
            self.logger.error(f"Error in _check_liability_threshold: {str(e)}")
            return {'approved': False, 'error': 'Liability check failed'}
    
    def _check_user_risk_limits(self, user_id: str, stake_amount: Decimal) -> Dict:
        """Kiểm tra giới hạn rủi ro của user"""
        try:
            # Lấy cấu hình rủi ro cho user
            user_config = RiskConfiguration.objects.filter(
                config_key='user_risk_limits',
                config_value__user_id=user_id,
                is_active=True
            ).first()
            
            if not user_config:
                # Sử dụng giới hạn mặc định
                max_stake = Decimal('1000.00')  # $1,000 mặc định
                daily_limit = Decimal('5000.00')  # $5,000 mặc định
            else:
                config = user_config.config_value
                max_stake = Decimal(str(config.get('max_stake', '1000.00')))
                daily_limit = Decimal(str(config.get('daily_limit', '5000.00')))
            
            # Kiểm tra stake amount
            if stake_amount > max_stake:
                return {
                    'approved': False,
                    'status': 'STAKE_EXCEEDS_LIMIT',
                    'max_stake': float(max_stake),
                    'requested_stake': float(stake_amount)
                }
            
            # Kiểm tra daily limit
            today_stake = self._calculate_user_daily_stake(user_id)
            if today_stake + stake_amount > daily_limit:
                return {
                    'approved': False,
                    'status': 'DAILY_LIMIT_EXCEEDED',
                    'daily_limit': float(daily_limit),
                    'today_stake': float(today_stake),
                    'requested_stake': float(stake_amount)
                }
            
            return {
                'approved': True,
                'status': 'WITHIN_LIMITS',
                'max_stake': float(max_stake),
                'daily_limit': float(daily_limit),
                'today_stake': float(today_stake)
            }
            
        except Exception as e:
            self.logger.error(f"Error in _check_user_risk_limits: {str(e)}")
            return {'approved': False, 'status': 'CHECK_FAILED'}
    
    def _check_market_status(self, match_id: str) -> Dict:
        """Kiểm tra trạng thái thị trường"""
        try:
            # Kiểm tra xem có suspension nào đang hoạt động không
            active_suspension = TradingSuspension.objects.filter(
                market_identifier=match_id,
                is_active=True,
                suspension_end__gt=timezone.now()
            ).first()
            
            if active_suspension:
                return {
                    'approved': False,
                    'status': 'MARKET_SUSPENDED',
                    'suspension_reason': active_suspension.reason,
                    'suspension_end': active_suspension.suspension_end.isoformat()
                }
            
            # Kiểm tra xem match có đang hoạt động không
            # Sử dụng Sports Data Service nếu có
            try:
                Match = get_sports_data_match()
                if Match:
                    match = Match.objects.get(id=match_id)
                    if match.status not in ['SCHEDULED', 'LIVE']:
                        return {
                            'approved': False,
                            'status': 'MATCH_NOT_ACTIVE',
                            'match_status': match.status
                        }
            except Exception:
                # Fallback: Gọi API từ Sports Data Service
                try:
                    response = requests.get(
                        f"{getattr(settings, 'SPORTS_DATA_SERVICE_URL', 'http://sports-data-service:8000')}/api/matches/{match_id}/",
                        timeout=5
                    )
                    if response.status_code == 200:
                        match_data = response.json()
                        match_status = match_data.get('status', 'UNKNOWN')
                        
                        if match_status not in ['SCHEDULED', 'LIVE']:
                            return {
                                'approved': False,
                                'status': 'MATCH_NOT_ACTIVE',
                                'match_status': match_status
                            }
                    else:
                        self.logger.warning(f"Failed to get match status: {response.status_code}")
                        
                except Exception as api_error:
                    self.logger.warning(f"API call failed for match status: {api_error}")
                
                # Fallback cuối cùng: Kiểm tra cache hoặc giả định an toàn
                cache_key = f"match_status_{match_id}"
                cached_status = cache.get(cache_key)
                
                if cached_status and cached_status not in ['SCHEDULED', 'LIVE']:
                    return {
                        'approved': False,
                        'status': 'MATCH_NOT_ACTIVE',
                        'match_status': cached_status
                    }
                
                # Giả định an toàn: match đang hoạt động
                self.logger.info(f"Assuming match {match_id} is active (fallback mode)")
            
            return {
                'approved': True,
                'status': 'MARKET_ACTIVE'
            }
            
        except Exception as e:
            self.logger.error(f"Error in _check_market_status: {str(e)}")
            return {'approved': False, 'status': 'CHECK_FAILED'}
    
    def _calculate_current_liability(self, match_id: str, bet_type_id: str, outcome: str) -> Decimal:
        """Tính toán liability hiện tại cho một outcome"""
        try:
            # Query database để lấy tất cả bets cho outcome này
            # Sử dụng BetSelection model từ Betting Service nếu có
            try:
                BetSelection, _ = get_betting_models()
                if not BetSelection:
                    return Decimal('0.00')
                
                # Tính tổng potential payout cho outcome này
                selections = BetSelection.objects.filter(
                    match_id=match_id,
                    bet_type_id=bet_type_id,
                    outcome=outcome,
                    status__in=['ACTIVE', 'PENDING']
                )
                
                total_payout = sum(
                    selection.stake_amount * selection.odds_value 
                    for selection in selections
                )
                
                return Decimal(str(total_payout))
                
            except (ImportError, Exception):
                # Fallback: Sử dụng cache hoặc external API call
                cache_key = f"liability_{match_id}_{bet_type_id}_{outcome}"
                cached_liability = cache.get(cache_key)
                
                if cached_liability:
                    return Decimal(str(cached_liability))
                
                # Nếu không có cache, gọi API từ Betting Service
                try:
                    response = requests.get(
                        f"{getattr(settings, 'BETTING_SERVICE_URL', 'http://betting-service:8000')}/api/liability/{match_id}/{bet_type_id}/{outcome}/",
                        timeout=5
                    )
                    if response.status_code == 200:
                        data = response.json()
                        liability = Decimal(str(data.get('total_liability', '0.00')))
                        
                        # Cache kết quả trong 5 phút
                        cache.set(cache_key, float(liability), 300)
                        return liability
                except Exception as api_error:
                    self.logger.warning(f"API call failed for liability calculation: {api_error}")
                
                # Fallback cuối cùng: sử dụng RiskAuditLog để ước tính
                recent_bets = RiskAuditLog.objects.filter(
                    related_object_type='BET',
                    action_details__match_id=match_id,
                    action_details__bet_type_id=bet_type_id,
                    action_details__outcome=outcome,
                    created_at__gte=timezone.now() - timedelta(hours=24)
                ).order_by('-created_at')[:100]
                
                estimated_liability = Decimal('0.00')
                for bet_log in recent_bets:
                    bet_data = bet_log.action_details.get('bet_data', {})
                    stake = Decimal(str(bet_data.get('stake_amount', '0.00')))
                    odds = Decimal(str(bet_data.get('odds_value', '1.00')))
                    estimated_liability += stake * odds
                
                return estimated_liability
            
        except Exception as e:
            self.logger.error(f"Error in _calculate_current_liability: {str(e)}")
            return Decimal('0.00')
    
    def _calculate_user_daily_stake(self, user_id: str) -> Decimal:
        """Tính tổng stake của user trong ngày hôm nay"""
        try:
            today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)
            
            # Query database để lấy tổng stake của user hôm nay
            try:
                _, BetSlip = get_betting_models()
                if not BetSlip:
                    return Decimal('0.00')
                
                daily_stake = BetSlip.objects.filter(
                    user_id=user_id,
                    created_at__gte=today_start,
                    created_at__lt=today_end,
                    status__in=['ACTIVE', 'PENDING', 'WON', 'LOST']
                ).aggregate(
                    total_stake=Sum('total_stake')
                )['total_stake'] or Decimal('0.00')
                
                return Decimal(str(daily_stake))
                
            except (ImportError, Exception):
                # Fallback: Sử dụng cache
                cache_key = f"user_daily_stake_{user_id}_{today_start.date()}"
                cached_stake = cache.get(cache_key)
                
                if cached_stake:
                    return Decimal(str(cached_stake))
                
                # Nếu không có cache, gọi API từ Betting Service
                try:
                    response = requests.get(
                        f"{getattr(settings, 'BETTING_SERVICE_URL', 'http://betting-service:8000')}/api/users/{user_id}/daily-stake/",
                        params={'date': today_start.date().isoformat()},
                        timeout=5
                    )
                    if response.status_code == 200:
                        data = response.json()
                        daily_stake = Decimal(str(data.get('total_stake', '0.00')))
                        
                        # Cache kết quả trong 1 giờ
                        cache.set(cache_key, float(daily_stake), 3600)
                        return daily_stake
                except Exception as api_error:
                    self.logger.warning(f"API call failed for daily stake calculation: {api_error}")
                
                # Fallback cuối cùng: sử dụng RiskAuditLog để ước tính
                recent_bets = RiskAuditLog.objects.filter(
                    related_object_type='BET',
                    action_details__user_id=user_id,
                    created_at__gte=today_start,
                    created_at__lt=today_end
                ).order_by('-created_at')[:200]
                
                estimated_stake = Decimal('0.00')
                for bet_log in recent_bets:
                    bet_data = bet_log.action_details.get('bet_data', {})
                    stake = Decimal(str(bet_data.get('stake_amount', '0.00')))
                    estimated_stake += stake
                
                return estimated_stake
            
        except Exception as e:
            self.logger.error(f"Error in _calculate_user_daily_stake: {str(e)}")
            return Decimal('0.00')
    
    def _calculate_risk_level(self, liability_check: Dict, user_check: Dict, market_check: Dict) -> str:
        """Tính toán mức độ rủi ro tổng thể"""
        if not all([liability_check.get('approved'), user_check.get('approved'), market_check.get('approved')]):
            return 'HIGH'
        
        # Tính toán risk level dựa trên liability
        if 'remaining_capacity' in liability_check:
            remaining = liability_check['remaining_capacity']
            threshold = liability_check['threshold']
            utilization_rate = (threshold - remaining) / threshold
            
            if utilization_rate > 0.8:
                return 'MEDIUM'
            elif utilization_rate > 0.6:
                return 'LOW'
            else:
                return 'VERY_LOW'
        
        return 'UNKNOWN'
    
    def _generate_recommendations(self, liability_check: Dict, user_check: Dict, market_check: Dict) -> List[str]:
        """Tạo ra các khuyến nghị dựa trên kết quả kiểm tra"""
        recommendations = []
        
        if not liability_check.get('approved'):
            recommendations.append("Giảm số tiền cược để giảm rủi ro")
            recommendations.append("Chọn outcome khác có rủi ro thấp hơn")
        
        if not user_check.get('approved'):
            if user_check.get('status') == 'STAKE_EXCEEDS_LIMIT':
                recommendations.append(f"Giảm số tiền cược xuống dưới ${user_check.get('max_stake', 0)}")
            elif user_check.get('status') == 'DAILY_LIMIT_EXCEEDED':
                recommendations.append("Đã đạt giới hạn cược hàng ngày")
        
        if not market_check.get('approved'):
            if market_check.get('status') == 'MARKET_SUSPENDED':
                recommendations.append("Thị trường đang tạm dừng, vui lòng thử lại sau")
            elif market_check.get('status') == 'MATCH_NOT_ACTIVE':
                recommendations.append("Trận đấu không còn nhận cược")
        
        if not recommendations:
            recommendations.append("Bet được chấp nhận, rủi ro trong ngưỡng cho phép")
        
        return recommendations
    
    def _get_rejection_reason(self, liability_check: Dict, user_check: Dict, market_check: Dict) -> str:
        """Lấy lý do từ chối chính"""
        if not liability_check.get('approved'):
            return f"Vượt quá ngưỡng rủi ro: ${liability_check.get('exceeds_by', 0):.2f}"
        elif not user_check.get('approved'):
            if user_check.get('status') == 'STAKE_EXCEEDS_LIMIT':
                return f"Vượt quá giới hạn cược tối đa: ${user_check.get('max_stake', 0):.2f}"
            elif user_check.get('status') == 'DAILY_LIMIT_EXCEEDED':
                return "Đã đạt giới hạn cược hàng ngày"
        elif not market_check.get('approved'):
            if market_check.get('status') == 'MARKET_SUSPENDED':
                return "Thị trường đang tạm dừng giao dịch"
            elif market_check.get('status') == 'MATCH_NOT_ACTIVE':
                return "Trận đấu không còn nhận cược"
        
        return "Không xác định được lý do từ chối"
    
    def _log_risk_check_audit(self, bet_data: Dict, result: Dict):
        """Ghi log audit cho risk check"""
        try:
            RiskAuditLog.objects.create(
                action_type='RISK_CHECK',
                description=f"Risk check for bet: {bet_data.get('user_id')} - {bet_data.get('match_id')}",
                related_object_type='BET',
                related_object_id=f"{bet_data.get('user_id')}_{bet_data.get('match_id')}",
                action_details={
                    'bet_data': bet_data,
                    'risk_result': result,
                    'timestamp': timezone.now().isoformat()
                }
            )
        except Exception as e:
            self.logger.error(f"Error logging risk check audit: {str(e)}")


class LiveOddsService:
    """Service cung cấp live odds cho cash out"""
    
    def __init__(self):
        self.logger = logging.getLogger('risk_manager')
    
    def get_live_odds(self, odds_request: Dict) -> Dict:
        """Lấy live odds cho một selection"""
        try:
            match_id = odds_request['match_id']
            bet_type_id = odds_request['bet_type_id']
            outcome = odds_request['outcome']
            
            # Trong thực tế, cần tích hợp với sports data provider
            # Đây là logic mẫu
            live_odds = self._calculate_live_odds(match_id, bet_type_id, outcome)
            
            return {
                'match_id': match_id,
                'bet_type_id': bet_type_id,
                'outcome': outcome,
                'live_odds': float(live_odds),
                'confidence_score': 0.85,
                'is_reliable_for_cashout': True,
                'last_updated': timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in get_live_odds: {str(e)}")
            return {
                'error': 'Failed to get live odds',
                'live_odds': None
            }
    
    def _calculate_live_odds(self, match_id: str, bet_type_id: str, outcome: str) -> Decimal:
        """Tính toán live odds dựa trên match progress"""
        # Logic mẫu - trong thực tế cần tích hợp với sports data
        base_odds = Decimal('2.00')
        
        # Giả sử có thông tin về match progress
        # Điều chỉnh odds dựa trên thời gian và tình huống trận đấu
        
        return base_odds


class EventMarginService:
    """Service cung cấp event margin cho cash out"""
    
    def __init__(self):
        self.logger = logging.getLogger('risk_manager')
    
    def get_event_margin(self, match_id: str) -> Dict:
        """Lấy event margin cho một match"""
        try:
            # Lấy cấu hình margin từ RiskConfiguration
            margin_config = RiskConfiguration.objects.filter(
                config_key='event_margin',
                config_value__match_id=match_id,
                is_active=True
            ).first()
            
            if margin_config:
                margin = margin_config.config_value.get('margin', 0.05)
            else:
                # Sử dụng margin mặc định
                margin = 0.05  # 5%
            
            return {
                'match_id': match_id,
                'effective_margin': float(margin),
                'margin_type': 'PERCENTAGE',
                'last_updated': timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error in get_event_margin: {str(e)}")
            return {
                'match_id': match_id,
                'effective_margin': 0.05,  # Default 5%
                'margin_type': 'PERCENTAGE',
                'error': 'Using default margin due to error'
            }

class LiabilityCalculationService:
    """Service tính toán Trách Nhiệm RÒNG hoàn chỉnh theo công thức yêu cầu"""
    
    def __init__(self):
        self.logger = logging.getLogger('risk_manager')
    
    def calculate_net_liability(self, match_id: str, bet_type_id: str, outcome: str) -> Dict:
        """
        Tính toán Trách Nhiệm RÒNG theo công thức:
        Trách nhiệm RÒNG nếu "Kết quả X" xảy ra = 
        (Tổng Payout nếu X xảy ra bao gồm cả PROMOTION) - 
        (Tổng Tiền Cược vào TẤT CẢ CÁC KẾT QUẢ CÒN LẠI)
        """
        try:
            # Lấy tất cả outcomes cho bet type này
            all_outcomes = self._get_all_outcomes_for_bet_type(bet_type_id)
            
            # Tính toán cho từng outcome
            liability_results = {}
            for current_outcome in all_outcomes:
                net_liability = self._calculate_outcome_net_liability(
                    match_id, bet_type_id, current_outcome, all_outcomes
                )
                liability_results[current_outcome] = net_liability
            
            return {
                'match_id': match_id,
                'bet_type_id': bet_type_id,
                'calculated_at': timezone.now().isoformat(),
                'liability_breakdown': liability_results,
                'total_exposure': sum(result['net_liability'] for result in liability_results.values())
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating net liability: {str(e)}")
            return {'error': f'Liability calculation failed: {str(e)}'}
    
    def _calculate_outcome_net_liability(self, match_id: str, bet_type_id: str, 
                                       target_outcome: str, all_outcomes: List[str]) -> Dict:
        """Tính toán net liability cho một outcome cụ thể"""
        try:
            # 1. Tính Tổng Payout nếu target_outcome thắng (bao gồm cả PROMOTION)
            total_payout_if_target_wins = self._calculate_total_payout_with_promotions(
                match_id, bet_type_id, target_outcome
            )
            
            # 2. Tính Tổng Tiền Cược vào TẤT CẢ CÁC KẾT QUẢ CÒN LẠI
            total_stake_other_outcomes = self._calculate_total_stake_other_outcomes(
                match_id, bet_type_id, target_outcome, all_outcomes
            )
            
            # 3. Tính Trách Nhiệm RÒNG
            net_liability = total_payout_if_target_wins - total_stake_other_outcomes
            
            return {
                'outcome': target_outcome,
                'total_payout_if_wins': float(total_payout_if_target_wins),
                'total_stake_other_outcomes': float(total_stake_other_outcomes),
                'net_liability': float(net_liability),
                'risk_level': self._determine_risk_level(net_liability)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating outcome liability: {str(e)}")
            return {'error': f'Outcome calculation failed: {str(e)}'}
    
    def _calculate_total_payout_with_promotions(self, match_id: str, bet_type_id: str, 
                                              outcome: str) -> Decimal:
        """Tính tổng payout bao gồm cả promotions"""
        try:
            # Lấy tất cả bets cho outcome này
            bets_for_outcome = self._get_bets_for_outcome(match_id, bet_type_id, outcome)
            
            total_payout = Decimal('0.00')
            
            for bet in bets_for_outcome:
                # Payout cơ bản: stake × odds
                basic_payout = bet['stake_amount'] * bet['odds_at_bet_time']
                
                # Payout từ promotions (nếu có)
                promotion_payout = self._calculate_promotion_payout(bet)
                
                # Tổng payout cho bet này
                bet_total_payout = basic_payout + promotion_payout
                total_payout += bet_total_payout
            
            return total_payout
            
        except Exception as e:
            self.logger.error(f"Error calculating total payout: {str(e)}")
            return Decimal('0.00')
    
    def _calculate_promotion_payout(self, bet: Dict) -> Decimal:
        """Tính toán payout từ promotions"""
        try:
            promotion_payout = Decimal('0.00')
            
            # Kiểm tra các loại promotion
            if bet.get('bonus_odds_multiplier'):
                # Bonus Odds: Tăng tỷ lệ cược
                bonus_multiplier = Decimal(str(bet['bonus_odds_multiplier']))
                promotion_payout += bet['stake_amount'] * (bonus_multiplier - Decimal('1.00'))
            
            if bet.get('free_bet_amount'):
                # Free Bet: Tiền thưởng từ cược miễn phí
                free_bet_amount = Decimal(str(bet['free_bet_amount']))
                promotion_payout += free_bet_amount
            
            if bet.get('gift_money_amount'):
                # Gift Money: Tiền thưởng
                gift_amount = Decimal(str(bet['gift_money_amount']))
                promotion_payout += gift_amount
            
            if bet.get('cashback_percentage'):
                # Cashback: Hoàn tiền theo %
                cashback_percent = Decimal(str(bet['cashback_percentage'])) / Decimal('100.00')
                promotion_payout += bet['stake_amount'] * cashback_percent
            
            return promotion_payout
            
        except Exception as e:
            self.logger.error(f"Error calculating promotion payout: {str(e)}")
            return Decimal('0.00')
    
    def _calculate_total_stake_other_outcomes(self, match_id: str, bet_type_id: str,
                                            target_outcome: str, all_outcomes: List[str]) -> Decimal:
        """Tính tổng tiền cược vào các outcomes khác"""
        try:
            total_stake = Decimal('0.00')
            
            for outcome in all_outcomes:
                if outcome != target_outcome:
                    outcome_stakes = self._get_total_stake_for_outcome(match_id, bet_type_id, outcome)
                    total_stake += outcome_stakes
            
            return total_stake
            
        except Exception as e:
            self.logger.error(f"Error calculating other outcomes stake: {str(e)}")
            return Decimal('0.00')
    
    def _get_all_outcomes_for_bet_type(self, bet_type_id: str) -> List[str]:
        """Lấy tất cả outcomes cho một bet type"""
        # Trong thực tế, cần query từ betting service
        # Đây là mapping mẫu
        bet_type_outcomes = {
            'MATCH_RESULT': ['HOME_WIN', 'AWAY_WIN', 'DRAW'],
            'CORRECT_SCORE': ['1-0', '2-0', '2-1', '0-0', '1-1', '0-1', '0-2', '1-2'],
            'TOTAL_GOALS': ['OVER_0.5', 'UNDER_0.5', 'OVER_1.5', 'UNDER_1.5', 'OVER_2.5', 'UNDER_2.5'],
            'BOTH_TEAMS_SCORE': ['YES', 'NO'],
            'FIRST_GOAL': ['HOME_TEAM', 'AWAY_TEAM', 'NO_GOAL']
        }
        
        return bet_type_outcomes.get(bet_type_id, ['DEFAULT_OUTCOME'])
    
    def _get_bets_for_outcome(self, match_id: str, bet_type_id: str, outcome: str) -> List[Dict]:
        """Lấy tất cả bets cho một outcome (cần tích hợp với betting service)"""
        # Trong thực tế, cần gọi API từ betting service
        # Đây là dữ liệu mẫu để test
        return [
            {
                'stake_amount': Decimal('100.00'),
                'odds_at_bet_time': Decimal('2.50'),
                'bonus_odds_multiplier': Decimal('1.20'),
                'free_bet_amount': Decimal('0.00'),
                'gift_money_amount': Decimal('0.00'),
                'cashback_percentage': Decimal('0.00')
            },
            {
                'stake_amount': Decimal('50.00'),
                'odds_at_bet_time': Decimal('2.40'),
                'bonus_odds_multiplier': Decimal('0.00'),
                'free_bet_amount': Decimal('25.00'),
                'gift_money_amount': Decimal('0.00'),
                'cashback_percentage': Decimal('0.00')
            }
        ]
    
    def _get_total_stake_for_outcome(self, match_id: str, bet_type_id: str, outcome: str) -> Decimal:
        """Lấy tổng stake cho một outcome (cần tích hợp với betting service)"""
        # Trong thực tế, cần gọi API từ betting service
        # Đây là dữ liệu mẫu để test
        sample_stakes = {
            'HOME_WIN': Decimal('500.00'),
            'AWAY_WIN': Decimal('300.00'),
            'DRAW': Decimal('200.00'),
            '1-0': Decimal('150.00'),
            '2-0': Decimal('100.00'),
            '2-1': Decimal('80.00'),
            '0-0': Decimal('120.00'),
            '1-1': Decimal('90.00'),
            '0-1': Decimal('70.00'),
            '0-2': Decimal('60.00'),
            '1-2': Decimal('50.00')
        }
        
        return sample_stakes.get(outcome, Decimal('0.00'))
    
    def _determine_risk_level(self, net_liability: Decimal) -> str:
        """Xác định mức độ rủi ro dựa trên net liability"""
        if net_liability <= Decimal('0.00'):
            return 'PROFIT'  # Có lãi
        elif net_liability <= Decimal('1000.00'):
            return 'LOW'
        elif net_liability <= Decimal('5000.00'):
            return 'MEDIUM'
        elif net_liability <= Decimal('10000.00'):
            return 'HIGH'
        else:
            return 'CRITICAL'

class VigorishMarginService:
    """Service thiết lập biên lợi nhuận nhà cái (Vigorish/Margin)"""
    
    def __init__(self):
        self.logger = logging.getLogger('risk_manager')
        self.default_margin = Decimal('0.05')  # 5% mặc định
    
    def calculate_odds_with_margin(self, true_probabilities: Dict[str, float], 
                                 target_margin: Decimal = None) -> Dict[str, Decimal]:
        """
        Tính toán tỷ lệ cược với margin đảm bảo lợi nhuận
        
        Args:
            true_probabilities: Dict với key là outcome, value là xác suất thật (0-1)
            target_margin: Margin mong muốn (ví dụ: 0.05 = 5%)
        
        Returns:
            Dict với key là outcome, value là tỷ lệ cược đã áp dụng margin
        """
        try:
            if not target_margin:
                target_margin = self.default_margin
            
            # Kiểm tra xác suất hợp lệ
            total_prob = sum(true_probabilities.values())
            if abs(total_prob - 1.0) > 0.01:  # Cho phép sai số 1%
                raise ValueError(f"Tổng xác suất phải = 1.0, hiện tại: {total_prob}")
            
            # Tính margin factor để đảm bảo tổng xác suất nghịch đảo > 100%
            margin_factor = Decimal('1.0') + target_margin
            
            # Tính tỷ lệ cược mới
            adjusted_odds = {}
            for outcome, probability in true_probabilities.items():
                # Công thức: Odds = 1 / (Probability / Margin_Factor)
                adjusted_probability = probability / float(margin_factor)
                adjusted_odds[outcome] = Decimal('1.0') / Decimal(str(adjusted_probability))
            
            # Kiểm tra tổng xác suất nghịch đảo
            total_inverse_prob = sum(Decimal('1.0') / odds for odds in adjusted_odds.values())
            actual_margin = (total_inverse_prob - Decimal('1.0')) / Decimal('1.0')
            
            return {
                'adjusted_odds': adjusted_odds,
                'target_margin': float(target_margin),
                'actual_margin': float(actual_margin),
                'margin_accuracy': float(abs(target_margin - actual_margin)),
                'total_inverse_probability': float(total_inverse_prob),
                'is_profitable': total_inverse_prob > Decimal('1.0')
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating odds with margin: {str(e)}")
            return {'error': f'Margin calculation failed: {str(e)}'}
    
    def calculate_football_match_odds(self, home_team_strength: float, away_team_strength: float,
                                    draw_probability: float = None, target_margin: Decimal = None) -> Dict:
        """
        Tính toán tỷ lệ cược cho trận đấu bóng đá với margin
        
        Args:
            home_team_strength: Sức mạnh đội nhà (0-1)
            away_team_strength: Sức mạnh đội khách (0-1)
            draw_probability: Xác suất hòa (nếu None sẽ tính tự động)
            target_margin: Margin mong muốn
        """
        try:
            # Tính xác suất cơ bản
            total_strength = home_team_strength + away_team_strength
            
            # Xác suất thắng dựa trên sức mạnh tương đối
            home_win_prob = home_team_strength / total_strength * 0.7  # 70% dựa trên sức mạnh
            away_win_prob = away_team_strength / total_strength * 0.7  # 70% dựa trên sức mạnh
            
            # Xác suất hòa
            if draw_probability is None:
                draw_probability = 1.0 - home_win_prob - away_win_prob
                # Đảm bảo xác suất hòa không âm
                if draw_probability < 0:
                    draw_probability = 0.1
                    # Điều chỉnh lại xác suất thắng
                    adjustment_factor = 0.9 / (home_win_prob + away_win_prob)
                    home_win_prob *= adjustment_factor
                    away_win_prob *= adjustment_factor
            
            # Chuẩn hóa để tổng = 1.0
            total_prob = home_win_prob + away_win_prob + draw_probability
            home_win_prob /= total_prob
            away_win_prob /= total_prob
            draw_probability /= total_prob
            
            true_probabilities = {
                'HOME_WIN': home_win_prob,
                'AWAY_WIN': away_win_prob,
                'DRAW': draw_probability
            }
            
            # Tính tỷ lệ cược với margin
            result = self.calculate_odds_with_margin(true_probabilities, target_margin)
            
            # Thêm thông tin bổ sung
            result['true_probabilities'] = true_probabilities
            result['team_analysis'] = {
                'home_team_strength': home_team_strength,
                'away_team_strength': away_team_strength,
                'strength_difference': abs(home_team_strength - away_team_strength)
            }
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating football odds: {str(e)}")
            return {'error': f'Football odds calculation failed: {str(e)}'}
    
    def calculate_correct_score_odds(self, expected_home_goals: float, expected_away_goals: float,
                                   target_margin: Decimal = None) -> Dict:
        """
        Tính toán tỷ lệ cược tỷ số chính xác sử dụng Phân phối Poisson
        
        Args:
            expected_home_goals: Số bàn thắng kỳ vọng của đội nhà
            expected_away_goals: Số bàn thắng kỳ vọng của đội khách
            target_margin: Margin mong muốn
        """
        try:
            # Sử dụng Phân phối Poisson để tính xác suất tỷ số
            score_probabilities = {}
            
            # Giới hạn số bàn thắng để tính toán (0-5 cho mỗi đội)
            max_goals = 5
            
            for home_goals in range(max_goals + 1):
                for away_goals in range(max_goals + 1):
                    # Tính xác suất theo Poisson
                    home_prob = self._poisson_probability(home_goals, expected_home_goals)
                    away_prob = self._poisson_probability(away_goals, expected_away_goals)
                    
                    # Xác suất tỷ số = tích xác suất của 2 đội
                    score_prob = home_prob * away_prob
                    score_key = f"{home_goals}-{away_goals}"
                    
                    score_probabilities[score_key] = score_prob
            
            # Tính tỷ lệ cược với margin
            result = self.calculate_odds_with_margin(score_probabilities, target_margin)
            
            # Thêm thông tin bổ sung
            result['poisson_parameters'] = {
                'expected_home_goals': expected_home_goals,
                'expected_away_goals': expected_away_goals
            }
            result['top_scores'] = sorted(
                [(score, prob) for score, prob in score_probabilities.items()],
                key=lambda x: x[1],
                reverse=True
            )[:10]  # Top 10 tỷ số có xác suất cao nhất
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating correct score odds: {str(e)}")
            return {'error': f'Correct score calculation failed: {str(e)}'}
    
    def _poisson_probability(self, k: int, lambda_param: float) -> float:
        """
        Tính xác suất Poisson: P(k; λ) = (e^-λ * λ^k) / k!
        
        Args:
            k: Số sự kiện xảy ra
            lambda_param: Tham số lambda (số sự kiện kỳ vọng)
        """
        import math
        
        if lambda_param <= 0:
            return 0.0
        
        # Tính e^-λ
        exp_neg_lambda = math.exp(-lambda_param)
        
        # Tính λ^k
        lambda_power_k = lambda_param ** k
        
        # Tính k!
        k_factorial = math.factorial(k)
        
        # Tính xác suất
        probability = (exp_neg_lambda * lambda_power_k) / k_factorial
        
        return probability
    
    def validate_margin_setting(self, odds: Dict[str, Decimal]) -> Dict:
        """
        Kiểm tra xem margin setting có hợp lệ không
        
        Args:
            odds: Dict với key là outcome, value là tỷ lệ cược
        """
        try:
            # Tính tổng xác suất nghịch đảo
            total_inverse_prob = sum(Decimal('1.0') / odds_value for odds_value in odds.values())
            
            # Tính margin
            margin = (total_inverse_prob - Decimal('1.0')) / Decimal('1.0')
            
            # Kiểm tra tính hợp lệ
            is_valid = total_inverse_prob > Decimal('1.0')
            margin_percentage = float(margin) * 100
            
            return {
                'is_valid': is_valid,
                'total_inverse_probability': float(total_inverse_prob),
                'margin_percentage': margin_percentage,
                'is_profitable': is_valid,
                'recommendation': self._get_margin_recommendation(margin_percentage)
            }
            
        except Exception as e:
            self.logger.error(f"Error validating margin: {str(e)}")
            return {'error': f'Margin validation failed: {str(e)}'}
    
    def _get_margin_recommendation(self, margin_percentage: float) -> str:
        """Đưa ra khuyến nghị về margin"""
        if margin_percentage < 2.0:
            return "Margin quá thấp, có thể gây lỗ. Khuyến nghị tăng lên 3-5%"
        elif margin_percentage < 5.0:
            return "Margin ở mức thấp, phù hợp cho thị trường cạnh tranh"
        elif margin_percentage < 10.0:
            return "Margin ở mức trung bình, cân bằng giữa lợi nhuận và cạnh tranh"
        elif margin_percentage < 15.0:
            return "Margin ở mức cao, đảm bảo lợi nhuận tốt"
        else:
            return "Margin rất cao, có thể ảnh hưởng đến khả năng cạnh tranh"

class PromotionRiskService:
    """Service quản lý rủi ro cho hệ thống khuyến mãi (Promotions)"""
    
    def __init__(self):
        self.logger = logging.getLogger('risk_manager')
    
    def calculate_promotion_risk(self, promotion_data: Dict) -> Dict:
        """
        Tính toán rủi ro cho một promotion
        
        Args:
            promotion_data: Dữ liệu promotion bao gồm type, parameters, etc.
        """
        try:
            promotion_type = promotion_data.get('type')
            
            if promotion_type == 'BONUS_ODDS':
                return self._calculate_bonus_odds_risk(promotion_data)
            elif promotion_type == 'FREE_BET':
                return self._calculate_free_bet_risk(promotion_data)
            elif promotion_type == 'GIFT_MONEY':
                return self._calculate_gift_money_risk(promotion_data)
            elif promotion_type == 'CASHBACK':
                return self._calculate_cashback_risk(promotion_data)
            else:
                return {'error': f'Unknown promotion type: {promotion_type}'}
                
        except Exception as e:
            self.logger.error(f"Error calculating promotion risk: {str(e)}")
            return {'error': f'Promotion risk calculation failed: {str(e)}'}
    
    def _calculate_bonus_odds_risk(self, promotion_data: Dict) -> Dict:
        """Tính toán rủi ro cho Bonus Odds (loại nguy hiểm nhất)"""
        try:
            base_odds = Decimal(str(promotion_data.get('base_odds', '2.00')))
            bonus_multiplier = Decimal(str(promotion_data.get('bonus_multiplier', '1.20')))
            stake_amount = Decimal(str(promotion_data.get('stake_amount', '100.00')))
            
            # Tính toán payout tăng thêm
            original_payout = stake_amount * base_odds
            bonus_payout = stake_amount * (base_odds * bonus_multiplier)
            additional_liability = bonus_payout - original_payout
            
            # Đánh giá mức độ rủi ro
            risk_level = self._assess_bonus_odds_risk(bonus_multiplier, additional_liability)
            
            return {
                'promotion_type': 'BONUS_ODDS',
                'risk_level': risk_level,
                'original_payout': float(original_payout),
                'bonus_payout': float(bonus_payout),
                'additional_liability': float(additional_liability),
                'risk_multiplier': float(bonus_multiplier),
                'recommendations': self._get_bonus_odds_recommendations(risk_level, bonus_multiplier)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating bonus odds risk: {str(e)}")
            return {'error': f'Bonus odds risk calculation failed: {str(e)}'}
    
    def _calculate_free_bet_risk(self, promotion_data: Dict) -> Dict:
        """Tính toán rủi ro cho Free Bet"""
        try:
            free_bet_amount = Decimal(str(promotion_data.get('free_bet_amount', '25.00')))
            odds_value = Decimal(str(promotion_data.get('odds_value', '2.00')))
            
            # Free Bet tạo ra "trách nhiệm ảo" không được bù đắp bằng tiền cược thật
            potential_winnings = free_bet_amount * odds_value
            net_liability = potential_winnings  # Không có stake để bù đắp
            
            # Đánh giá rủi ro
            risk_level = self._assess_free_bet_risk(free_bet_amount, net_liability)
            
            return {
                'promotion_type': 'FREE_BET',
                'risk_level': risk_level,
                'free_bet_amount': float(free_bet_amount),
                'potential_winnings': float(potential_winnings),
                'net_liability': float(net_liability),
                'recommendations': self._get_free_bet_recommendations(risk_level, free_bet_amount)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating free bet risk: {str(e)}")
            return {'error': f'Free bet risk calculation failed: {str(e)}'}
    
    def _calculate_gift_money_risk(self, promotion_data: Dict) -> Dict:
        """Tính toán rủi ro cho Gift Money"""
        try:
            gift_amount = Decimal(str(promotion_data.get('gift_amount', '50.00')))
            wagering_requirement = Decimal(str(promotion_data.get('wagering_requirement', '3.00')))
            
            # Gift Money hoạt động như tiền thật sau khi đáp ứng điều kiện
            effective_liability = gift_amount * wagering_requirement
            
            # Đánh giá rủi ro
            risk_level = self._assess_gift_money_risk(gift_amount, effective_liability)
            
            return {
                'promotion_type': 'GIFT_MONEY',
                'risk_level': risk_level,
                'gift_amount': float(gift_amount),
                'wagering_requirement': float(wagering_requirement),
                'effective_liability': float(effective_liability),
                'recommendations': self._get_gift_money_recommendations(risk_level, gift_amount)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating gift money risk: {str(e)}")
            return {'error': f'Gift money risk calculation failed: {str(e)}'}
    
    def _calculate_cashback_risk(self, promotion_data: Dict) -> Dict:
        """Tính toán rủi ro cho Cashback"""
        try:
            cashback_percentage = Decimal(str(promotion_data.get('cashback_percentage', '10.00')))
            stake_amount = Decimal(str(promotion_data.get('stake_amount', '100.00')))
            
            # Cashback tác động gián tiếp, làm giảm Lợi Nhuận Gộp Thực Tế
            cashback_amount = stake_amount * (cashback_percentage / Decimal('100.00'))
            
            # Đánh giá rủi ro
            risk_level = self._assess_cashback_risk(cashback_percentage, cashback_amount)
            
            return {
                'promotion_type': 'CASHBACK',
                'risk_level': risk_level,
                'cashback_percentage': float(cashback_percentage),
                'cashback_amount': float(cashback_amount),
                'profit_reduction': float(cashback_amount),
                'recommendations': self._get_cashback_recommendations(risk_level, cashback_percentage)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating cashback risk: {str(e)}")
            return {'error': f'Cashback risk calculation failed: {str(e)}'}
    
    def _assess_bonus_odds_risk(self, bonus_multiplier: Decimal, additional_liability: Decimal) -> str:
        """Đánh giá mức độ rủi ro cho Bonus Odds"""
        if bonus_multiplier >= Decimal('2.00'):
            return 'CRITICAL'
        elif bonus_multiplier >= Decimal('1.50'):
            return 'HIGH'
        elif bonus_multiplier >= Decimal('1.30'):
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _assess_free_bet_risk(self, free_bet_amount: Decimal, net_liability: Decimal) -> str:
        """Đánh giá mức độ rủi ro cho Free Bet"""
        if free_bet_amount >= Decimal('100.00'):
            return 'HIGH'
        elif free_bet_amount >= Decimal('50.00'):
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _assess_gift_money_risk(self, gift_amount: Decimal, effective_liability: Decimal) -> str:
        """Đánh giá mức độ rủi ro cho Gift Money"""
        if gift_amount >= Decimal('200.00'):
            return 'HIGH'
        elif gift_amount >= Decimal('100.00'):
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _assess_cashback_risk(self, cashback_percentage: Decimal, cashback_amount: Decimal) -> str:
        """Đánh giá mức độ rủi ro cho Cashback"""
        if cashback_percentage >= Decimal('20.00'):
            return 'HIGH'
        elif cashback_percentage >= Decimal('10.00'):
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_bonus_odds_recommendations(self, risk_level: str, bonus_multiplier: Decimal) -> List[str]:
        """Đưa ra khuyến nghị cho Bonus Odds"""
        recommendations = []
        
        if risk_level == 'CRITICAL':
            recommendations.extend([
                "Giảm bonus multiplier xuống dưới 2.0x",
                "Áp dụng giới hạn stake tối đa",
                "Yêu cầu wagering requirement cao",
                "Theo dõi liên tục exposure"
            ])
        elif risk_level == 'HIGH':
            recommendations.extend([
                "Giới hạn số lượng promotion per user",
                "Áp dụng time limit cho promotion",
                "Theo dõi daily exposure"
            ])
        elif risk_level == 'MEDIUM':
            recommendations.extend([
                "Áp dụng wagering requirement vừa phải",
                "Giới hạn promotion cho VIP users"
            ])
        else:
            recommendations.append("Promotion an toàn, có thể áp dụng rộng rãi")
        
        return recommendations
    
    def _get_free_bet_recommendations(self, risk_level: str, free_bet_amount: Decimal) -> List[str]:
        """Đưa ra khuyến nghị cho Free Bet"""
        recommendations = []
        
        if risk_level == 'HIGH':
            recommendations.extend([
                "Giảm free bet amount xuống dưới $50",
                "Áp dụng wagering requirement 5x trở lên",
                "Giới hạn 1 free bet per user per day"
            ])
        elif risk_level == 'MEDIUM':
            recommendations.extend([
                "Áp dụng wagering requirement 3x",
                "Giới hạn free bet cho new users"
            ])
        else:
            recommendations.append("Free bet an toàn cho user acquisition")
        
        return recommendations
    
    def _get_gift_money_recommendations(self, risk_level: str, gift_amount: Decimal) -> List[str]:
        """Đưa ra khuyến nghị cho Gift Money"""
        recommendations = []
        
        if risk_level == 'HIGH':
            recommendations.extend([
                "Giảm gift amount xuống dưới $100",
                "Áp dụng wagering requirement 10x trở lên",
                "Chỉ áp dụng cho VIP users"
            ])
        elif risk_level == 'MEDIUM':
            recommendations.extend([
                "Áp dụng wagering requirement 5x",
                "Giới hạn gift money cho special events"
            ])
        else:
            recommendations.append("Gift money phù hợp cho loyalty program")
        
        return recommendations
    
    def _get_cashback_recommendations(self, risk_level: str, cashback_percentage: Decimal) -> List[str]:
        """Đưa ra khuyến nghị cho Cashback"""
        recommendations = []
        
        if risk_level == 'HIGH':
            recommendations.extend([
                "Giảm cashback percentage xuống dưới 10%",
                "Áp dụng giới hạn maximum cashback amount",
                "Chỉ áp dụng cho losing bets"
            ])
        elif risk_level == 'MEDIUM':
            recommendations.extend([
                "Áp dụng cashback cho specific bet types",
                "Giới hạn cashback cho daily/weekly basis"
            ])
        else:
            recommendations.append("Cashback phù hợp cho retention strategy")
        
        return recommendations
    
    def get_promotion_risk_summary(self, match_id: str) -> Dict:
        """Lấy tổng quan rủi ro promotion cho một match"""
        try:
            # Trong thực tế, cần query từ promotion service
            # Đây là dữ liệu mẫu để test
            sample_promotions = [
                {
                    'type': 'BONUS_ODDS',
                    'base_odds': '2.50',
                    'bonus_multiplier': '1.30',
                    'stake_amount': '100.00'
                },
                {
                    'type': 'FREE_BET',
                    'free_bet_amount': '25.00',
                    'odds_value': '2.00'
                },
                {
                    'type': 'GIFT_MONEY',
                    'gift_amount': '50.00',
                    'wagering_requirement': '3.00'
                }
            ]
            
            # Tính toán rủi ro cho từng promotion
            promotion_risks = []
            total_additional_liability = Decimal('0.00')
            
            for promotion in sample_promotions:
                risk_result = self.calculate_promotion_risk(promotion)
                if 'error' not in risk_result:
                    promotion_risks.append(risk_result)
                    
                    # Cộng dồn additional liability
                    if 'additional_liability' in risk_result:
                        total_additional_liability += Decimal(str(risk_result['additional_liability']))
                    elif 'net_liability' in risk_result:
                        total_additional_liability += Decimal(str(risk_result['net_liability']))
                    elif 'effective_liability' in risk_result:
                        total_additional_liability += Decimal(str(risk_result['effective_liability']))
            
            # Đánh giá tổng thể
            overall_risk_level = self._assess_overall_promotion_risk(promotion_risks)
            
            return {
                'match_id': match_id,
                'overall_risk_level': overall_risk_level,
                'total_promotions': len(promotion_risks),
                'total_additional_liability': float(total_additional_liability),
                'promotion_breakdown': promotion_risks,
                'risk_distribution': self._get_risk_distribution(promotion_risks),
                'recommendations': self._get_overall_recommendations(overall_risk_level, total_additional_liability)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting promotion risk summary: {str(e)}")
            return {'error': f'Promotion risk summary failed: {str(e)}'}
    
    def _assess_overall_promotion_risk(self, promotion_risks: List[Dict]) -> str:
        """Đánh giá mức độ rủi ro tổng thể của promotions"""
        if not promotion_risks:
            return 'LOW'
        
        risk_scores = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
        total_score = sum(risk_scores.get(risk['risk_level'], 1) for risk in promotion_risks)
        average_score = total_score / len(promotion_risks)
        
        if average_score >= 3.5:
            return 'CRITICAL'
        elif average_score >= 2.5:
            return 'HIGH'
        elif average_score >= 1.5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_risk_distribution(self, promotion_risks: List[Dict]) -> Dict[str, int]:
        """Lấy phân bố mức độ rủi ro"""
        distribution = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
        
        for risk in promotion_risks:
            risk_level = risk.get('risk_level', 'LOW')
            distribution[risk_level] += 1
        
        return distribution
    
    def _get_overall_recommendations(self, overall_risk_level: str, total_liability: Decimal) -> List[str]:
        """Đưa ra khuyến nghị tổng thể"""
        recommendations = []
        
        if overall_risk_level == 'CRITICAL':
            recommendations.extend([
                "Tạm dừng tất cả promotions có rủi ro cao",
                "Xem xét lại chiến lược promotion",
                "Tăng cường monitoring và controls"
            ])
        elif overall_risk_level == 'HIGH':
            recommendations.extend([
                "Giảm số lượng promotions đồng thời",
                "Áp dụng stricter wagering requirements",
                "Theo dõi exposure liên tục"
            ])
        elif overall_risk_level == 'MEDIUM':
            recommendations.extend([
                "Cân bằng giữa risk và reward",
                "Áp dụng standard controls"
            ])
        else:
            recommendations.append("Promotions an toàn, có thể mở rộng")
        
        return recommendations

class RiskThresholdService:
    """Service quản lý ngưỡng rủi ro cho các loại bet và match"""
    
    def __init__(self):
        self.logger = logging.getLogger('risk_manager')
    
    def set_risk_thresholds(self, match_id: str, bookmaker_type: str, 
                           main_threshold: Decimal, promotion_threshold: Decimal = None) -> Dict:
        """
        Thiết lập ngưỡng rủi ro cho một match
        
        Args:
            match_id: ID của trận đấu
            bookmaker_type: Loại nhà cái
            main_threshold: Trần Cố Định CHÍNH
            promotion_threshold: Trần Cố Định PHỤ
        """
        try:
            # Lưu vào database hoặc cache
            threshold_data = {
                'match_id': match_id,
                'bookmaker_type': bookmaker_type,
                'main_threshold': float(main_threshold),
                'promotion_threshold': float(promotion_threshold) if promotion_threshold else None,
                'created_at': timezone.now().isoformat(),
                'status': 'ACTIVE'
            }
            
            # Trong thực tế, cần lưu vào database
            # RiskConfiguration.objects.create(...)
            
            self.logger.info(f"Risk thresholds set for match {match_id}: {threshold_data}")
            return {
                'success': True,
                'thresholds': threshold_data,
                'message': 'Risk thresholds configured successfully'
            }
            
        except Exception as e:
            self.logger.error(f"Error setting risk thresholds: {str(e)}")
            return {'error': f'Failed to set risk thresholds: {str(e)}'}
    
    def check_risk_threshold(self, match_id: str, bet_type_id: str, outcome: str, 
                           stake_amount: Decimal) -> Dict:
        """
        Kiểm tra ngưỡng rủi ro cho một bet
        
        Args:
            match_id: ID của trận đấu
            bet_type_id: ID của loại bet
            outcome: Kết quả dự đoán
            stake_amount: Số tiền cược
        """
        try:
            # Trong thực tế, cần query từ database
            # thresholds = RiskConfiguration.objects.get(match_id=match_id)
            
            # Giả lập dữ liệu để test
            thresholds = {
                'main_threshold': Decimal('10000.00'),
                'promotion_threshold': Decimal('5000.00')
            }
            
            # Kiểm tra ngưỡng chính
            if stake_amount > thresholds['main_threshold']:
                return {
                    'threshold_exceeded': True,
                    'threshold_type': 'MAIN',
                    'current_amount': float(stake_amount),
                    'threshold_limit': float(thresholds['main_threshold']),
                    'excess_amount': float(stake_amount - thresholds['main_threshold']),
                    'risk_level': 'CRITICAL',
                    'recommendation': 'Bet vượt quá ngưỡng chính - cần xem xét lại'
                }
            
            # Kiểm tra ngưỡng promotion (nếu có)
            if thresholds.get('promotion_threshold') and stake_amount > thresholds['promotion_threshold']:
                return {
                    'threshold_exceeded': True,
                    'threshold_type': 'PROMOTION',
                    'current_amount': float(stake_amount),
                    'threshold_limit': float(thresholds['promotion_threshold']),
                    'excess_amount': float(stake_amount - thresholds['promotion_threshold']),
                    'risk_level': 'HIGH',
                    'recommendation': 'Bet vượt quá ngưỡng promotion - cần theo dõi'
                }
            
            # Bet trong ngưỡng an toàn
            return {
                'threshold_exceeded': False,
                'threshold_type': 'SAFE',
                'current_amount': float(stake_amount),
                'threshold_limit': float(thresholds['main_threshold']),
                'risk_level': 'LOW',
                'recommendation': 'Bet trong ngưỡng an toàn'
            }
            
        except Exception as e:
            self.logger.error(f"Error checking risk threshold: {str(e)}")
            return {'error': f'Failed to check risk threshold: {str(e)}'}
    
    def get_match_thresholds(self, match_id: str) -> Dict:
        """Lấy ngưỡng rủi ro cho một match"""
        try:
            # Trong thực tế, cần query từ database
            return {
                'match_id': match_id,
                'main_threshold': 10000.00,
                'promotion_threshold': 5000.00,
                'status': 'ACTIVE'
            }
        except Exception as e:
            self.logger.error(f"Error getting match thresholds: {str(e)}")
            return {'error': f'Failed to get match thresholds: {str(e)}'}


class InPlayRiskService:
    """Service quản lý rủi ro cho các bet in-play (live betting)"""
    
    def __init__(self):
        self.logger = logging.getLogger('risk_manager')
    
    def calculate_inplay_risk(self, match_id: str, bet_data: Dict, live_odds: Dict) -> Dict:
        """
        Tính toán rủi ro cho bet in-play
        
        Args:
            match_id: ID của trận đấu
            bet_data: Dữ liệu bet
            live_odds: Tỷ lệ cược hiện tại
        """
        try:
            # 1. Phân tích biến động odds
            odds_volatility = self._analyze_odds_volatility(live_odds)
            
            # 2. Đánh giá thời gian còn lại
            time_remaining = self._assess_time_remaining(match_id)
            
            # 3. Phân tích pattern betting
            betting_pattern = self._analyze_betting_pattern(match_id, bet_data)
            
            # 4. Tính toán rủi ro tổng hợp
            overall_risk = self._calculate_overall_inplay_risk(
                odds_volatility, time_remaining, betting_pattern
            )
            
            return {
                'match_id': match_id,
                'odds_volatility': odds_volatility,
                'time_remaining': time_remaining,
                'betting_pattern': betting_pattern,
                'overall_risk': overall_risk,
                'recommendations': self._get_inplay_recommendations(overall_risk)
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating inplay risk: {str(e)}")
            return {'error': f'Inplay risk calculation failed: {str(e)}'}
    
    def _analyze_odds_volatility(self, live_odds: Dict) -> Dict:
        """Phân tích biến động tỷ lệ cược"""
        try:
            # Giả lập dữ liệu để test
            volatility_score = 15.5  # 15.5% biến động
            
            if volatility_score >= 30:
                risk_level = 'CRITICAL'
            elif volatility_score >= 20:
                risk_level = 'HIGH'
            elif volatility_score >= 10:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            
            return {
                'volatility_score': volatility_score,
                'risk_level': risk_level,
                'description': f'Odds biến động {volatility_score:.1f}%'
            }
        except Exception as e:
            self.logger.error(f"Error analyzing odds volatility: {str(e)}")
            return {'error': f'Odds volatility analysis failed: {str(e)}'}
    
    def _assess_time_remaining(self, match_id: str) -> Dict:
        """Đánh giá thời gian còn lại của trận đấu"""
        try:
            # Trong thực tế, cần query từ match service
            # Giả lập dữ liệu để test
            match_duration = 90  # phút
            time_elapsed = 75    # phút
            time_remaining = match_duration - time_elapsed
            
            if time_remaining <= 5:
                risk_level = 'CRITICAL'
            elif time_remaining <= 15:
                risk_level = 'HIGH'
            elif time_remaining <= 30:
                risk_level = 'MEDIUM'
            else:
                risk_level = 'LOW'
            
            return {
                'match_duration': match_duration,
                'time_elapsed': time_elapsed,
                'time_remaining': time_remaining,
                'risk_level': risk_level,
                'description': f'Còn {time_remaining} phút'
            }
        except Exception as e:
            self.logger.error(f"Error assessing time remaining: {str(e)}")
            return {'error': f'Time assessment failed: {str(e)}'}
    
    def _analyze_betting_pattern(self, match_id: str, bet_data: Dict) -> Dict:
        """Phân tích pattern betting"""
        try:
            # Trong thực tế, cần query từ database
            # Giả lập dữ liệu để test
            total_bets = 150
            total_volume = 25000.00
            average_stake = total_volume / total_bets if total_bets > 0 else 0
            
            if total_volume > 50000:
                volume_risk = 'HIGH'
            elif total_volume > 25000:
                volume_risk = 'MEDIUM'
            else:
                volume_risk = 'LOW'
            
            return {
                'total_bets': total_bets,
                'total_volume': float(total_volume),
                'average_stake': float(average_stake),
                'volume_risk': volume_risk,
                'description': f'{total_bets} bets, tổng {total_volume:,.0f}'
            }
        except Exception as e:
            self.logger.error(f"Error analyzing betting pattern: {str(e)}")
            return {'error': f'Betting pattern analysis failed: {str(e)}'}
    
    def _calculate_overall_inplay_risk(self, odds_volatility: Dict, time_remaining: Dict, 
                                     betting_pattern: Dict) -> Dict:
        """Tính toán rủi ro tổng hợp cho in-play"""
        try:
            # Tính điểm rủi ro tổng hợp
            risk_scores = {
                'odds_volatility': self._get_risk_score(odds_volatility.get('risk_level', 'LOW')),
                'time_remaining': self._get_risk_score(time_remaining.get('risk_level', 'LOW')),
                'betting_pattern': self._get_risk_score(betting_pattern.get('volume_risk', 'LOW'))
            }
            
            total_score = sum(risk_scores.values())
            average_score = total_score / len(risk_scores)
            
            # Xác định mức độ rủi ro tổng thể
            if average_score >= 3.5:
                overall_risk = 'CRITICAL'
            elif average_score >= 2.5:
                overall_risk = 'HIGH'
            elif average_score >= 1.5:
                overall_risk = 'MEDIUM'
            else:
                overall_risk = 'LOW'
            
            return {
                'overall_risk': overall_risk,
                'risk_scores': risk_scores,
                'total_score': total_score,
                'average_score': average_score,
                'description': f'Rủi ro tổng hợp: {overall_risk}'
            }
        except Exception as e:
            self.logger.error(f"Error calculating overall inplay risk: {str(e)}")
            return {'error': f'Overall risk calculation failed: {str(e)}'}
    
    def _get_risk_score(self, risk_level: str) -> int:
        """Chuyển đổi mức độ rủi ro thành điểm số"""
        risk_scores = {
            'LOW': 1,
            'MEDIUM': 2,
            'HIGH': 3,
            'CRITICAL': 4
        }
        return risk_scores.get(risk_level, 1)
    
    def _get_inplay_recommendations(self, overall_risk: Dict) -> List[str]:
        """Đưa ra khuyến nghị cho in-play betting"""
        risk_level = overall_risk.get('overall_risk', 'LOW')
        recommendations = []
        
        if risk_level == 'CRITICAL':
            recommendations.extend([
                "Tạm dừng tất cả bet in-play",
                "Đóng market ngay lập tức",
                "Xem xét lại odds và limits"
            ])
        elif risk_level == 'HIGH':
            recommendations.extend([
                "Giảm limits cho bet in-play",
                "Tăng cường monitoring",
                "Xem xét đóng một số market"
            ])
        elif risk_level == 'MEDIUM':
            recommendations.extend([
                "Theo dõi biến động odds",
                "Kiểm tra limits định kỳ"
            ])
        else:
            recommendations.append("In-play betting an toàn")
        
        return recommendations


class BookmakerRoleManagementService:
    """Service quản lý vai trò nhà cái và áp dụng quy tắc rủi ro khác nhau"""
    
    def __init__(self):
        self.logger = logging.getLogger('risk_manager')
    
    def determine_bookmaker_role(self, user_id: str, match_id: str = None) -> Dict:
        """
        Xác định vai trò nhà cái cho một user
        
        Args:
            user_id: ID của user
            match_id: ID của match (nếu có)
        """
        try:
            # Trong thực tế, cần query từ user service và groups service
            # Đây là logic mẫu để test
            
            # Kiểm tra xem user có phải là system admin không
            if self._is_system_admin(user_id):
                return {
                    'role': 'SYSTEM',
                    'sub_role': 'SUPER_ADMIN',
                    'risk_rules': 'MANDATORY_SAFETY_RULES',
                    'description': 'System admin - áp dụng quy tắc an toàn mặc định'
                }
            
            # Kiểm tra xem user có phải là admin được chỉ định không
            elif self._is_designated_admin(user_id):
                return {
                    'role': 'SYSTEM',
                    'sub_role': 'DESIGNATED_ADMIN',
                    'risk_rules': 'MANDATORY_SAFETY_RULES',
                    'description': 'Designated admin - áp dụng quy tắc an toàn mặc định'
                }
            
            # Kiểm tra xem user có phải là individual bookmaker không
            elif self._is_individual_bookmaker(user_id):
                risk_choice = self._get_individual_risk_choice(user_id, match_id)
                return {
                    'role': 'INDIVIDUAL',
                    'sub_role': 'PERSONAL',
                    'risk_rules': risk_choice['method'],
                    'risk_choice': risk_choice,
                    'description': f'Individual bookmaker - {risk_choice["method_display"]}'
                }
            
            # Kiểm tra xem user có phải là group bookmaker không
            elif self._is_group_bookmaker(user_id):
                group_risk_choice = self._get_group_risk_choice(user_id, match_id)
                return {
                    'role': 'GROUP',
                    'sub_role': 'GROUP_MEMBER',
                    'risk_rules': group_risk_choice['method'],
                    'risk_choice': group_risk_choice,
                    'description': f'Group bookmaker - {group_risk_choice["method_display"]}'
                }
            
            else:
                return {
                    'role': 'UNKNOWN',
                    'sub_role': 'UNKNOWN',
                    'risk_rules': 'DEFAULT',
                    'description': 'Unknown role - áp dụng quy tắc mặc định'
                }
                
        except Exception as e:
            self.logger.error(f"Error determining bookmaker role: {str(e)}")
            return {'error': f'Role determination failed: {str(e)}'}
    
    def apply_risk_rules_by_role(self, bookmaker_role: Dict, risk_data: Dict) -> Dict:
        """
        Áp dụng quy tắc rủi ro dựa trên vai trò nhà cái
        
        Args:
            bookmaker_role: Thông tin vai trò nhà cái
            risk_data: Dữ liệu rủi ro cần xử lý
        """
        try:
            role = bookmaker_role.get('role')
            risk_rules = bookmaker_role.get('risk_rules')
            
            if role == 'SYSTEM':
                # System admin - áp dụng quy tắc an toàn mặc định
                return self._apply_system_safety_rules(risk_data)
            
            elif role in ['INDIVIDUAL', 'GROUP']:
                # Individual/Group bookmaker - áp dụng theo lựa chọn
                if risk_rules == 'AUTO_PROTECTION':
                    return self._apply_auto_protection_rules(risk_data, bookmaker_role)
                elif risk_rules == 'MANUAL_MANAGEMENT':
                    return self._apply_manual_management_rules(risk_data, bookmaker_role)
                else:
                    return self._apply_default_rules(risk_data)
            
            else:
                # Unknown role - áp dụng quy tắc mặc định
                return self._apply_default_rules(risk_data)
                
        except Exception as e:
            self.logger.error(f"Error applying risk rules: {str(e)}")
            return {'error': f'Risk rules application failed: {str(e)}'}
    
    def _apply_system_safety_rules(self, risk_data: Dict) -> Dict:
        """Áp dụng quy tắc an toàn cho system admin"""
        try:
            # Bỏ qua mọi cài đặt tùy chỉnh, áp đặt quy tắc an toàn mặc định
            safety_rules = {
                'margin_enabled': True,
                'dynamic_odds_enabled': True,
                'risk_threshold_enabled': True,
                'auto_suspension_enabled': True,
                'promotion_risk_control': True,
                'inplay_risk_management': True,
                'default_margin': 0.05,  # 5%
                'default_risk_threshold': 10000.0,  # $10,000
                'description': 'System safety rules - bảo vệ tối đa'
            }
            
            return {
                'rules_applied': 'SYSTEM_SAFETY',
                'safety_rules': safety_rules,
                'risk_data_processed': risk_data,
                'recommendations': [
                    'Biên lợi nhuận luôn được kích hoạt',
                    'Dynamic Odds luôn được kích hoạt',
                    'Ngưỡng rủi ro tối đa luôn được áp dụng',
                    'Tự động tạm dừng khi vượt ngưỡng'
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error applying system safety rules: {str(e)}")
            return {'error': f'System safety rules failed: {str(e)}'}
    
    def _apply_auto_protection_rules(self, risk_data: Dict, bookmaker_role: Dict) -> Dict:
        """Áp dụng quy tắc bảo vệ tự động cho individual/group bookmaker"""
        try:
            risk_choice = bookmaker_role.get('risk_choice', {})
            risk_threshold = risk_choice.get('risk_threshold', 5000.0)
            
            auto_protection_rules = {
                'margin_enabled': True,
                'dynamic_odds_enabled': True,
                'risk_threshold_enabled': True,
                'auto_suspension_enabled': True,
                'promotion_risk_control': True,
                'inplay_risk_management': True,
                'user_defined_threshold': risk_threshold,
                'description': f'Auto protection - ngưỡng rủi ro: ${risk_threshold}'
            }
            
            return {
                'rules_applied': 'AUTO_PROTECTION',
                'auto_protection_rules': auto_protection_rules,
                'risk_data_processed': risk_data,
                'recommendations': [
                    'Kích hoạt bảo vệ tự động',
                    f'Ngưỡng rủi ro: ${risk_threshold}',
                    'Dynamic Odds được kích hoạt',
                    'Tự động tạm dừng khi vượt ngưỡng'
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error applying auto protection rules: {str(e)}")
            return {'error': f'Auto protection rules failed: {str(e)}'}
    
    def _apply_manual_management_rules(self, risk_data: Dict, bookmaker_role: Dict) -> Dict:
        """Áp dụng quy tắc quản lý thủ công cho individual/group bookmaker"""
        try:
            # Tự quản lý rủi ro thủ công - rủi ro cao
            manual_rules = {
                'margin_enabled': False,
                'dynamic_odds_enabled': False,
                'risk_threshold_enabled': False,
                'auto_suspension_enabled': False,
                'promotion_risk_control': False,
                'inplay_risk_management': False,
                'description': 'Manual management - tự quản lý rủi ro'
            }
            
            return {
                'rules_applied': 'MANUAL_MANAGEMENT',
                'manual_rules': manual_rules,
                'risk_data_processed': risk_data,
                'warnings': [
                    '⚠️ Rủi ro cao - không có bảo vệ tự động',
                    '⚠️ Toàn bộ vốn được coi là ngưỡng rủi ro',
                    '⚠️ Người dùng phải tự quản lý rủi ro',
                    '⚠️ Không có Dynamic Odds'
                ],
                'recommendations': [
                    'Theo dõi liên tục exposure',
                    'Thiết lập giới hạn thủ công',
                    'Sẵn sàng chấp nhận rủi ro cao'
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Error applying manual management rules: {str(e)}")
            return {'error': f'Manual management rules failed: {str(e)}'}
    
    def _apply_default_rules(self, risk_data: Dict) -> Dict:
        """Áp dụng quy tắc mặc định"""
        try:
            default_rules = {
                'margin_enabled': True,
                'dynamic_odds_enabled': False,
                'risk_threshold_enabled': True,
                'auto_suspension_enabled': False,
                'promotion_risk_control': False,
                'inplay_risk_management': False,
                'description': 'Default rules - cân bằng giữa an toàn và linh hoạt'
            }
            
            return {
                'rules_applied': 'DEFAULT',
                'default_rules': default_rules,
                'risk_data_processed': risk_data,
                'description': 'Áp dụng quy tắc mặc định'
            }
            
        except Exception as e:
            self.logger.error(f"Error applying default rules: {str(e)}")
            return {'error': f'Default rules failed: {str(e)}'}
    
    def validate_risk_management_choice(self, user_id: str, match_id: str, 
                                      choice_method: str, risk_threshold: Decimal = None) -> Dict:
        """
        Xác thực lựa chọn quản lý rủi ro của user
        
        Args:
            user_id: ID của user
            match_id: ID của match
            choice_method: Phương thức quản lý rủi ro
            risk_threshold: Ngưỡng rủi ro (nếu có)
        """
        try:
            # Kiểm tra xem user đã thực hiện lựa chọn chưa
            existing_choice = self._get_existing_risk_choice(user_id, match_id)
            
            if existing_choice:
                return {
                    'valid': False,
                    'error': 'User đã thực hiện lựa chọn quản lý rủi ro',
                    'existing_choice': existing_choice
                }
            
            # Xác thực phương thức
            valid_methods = ['AUTO_PROTECTION', 'MANUAL_MANAGEMENT']
            if choice_method not in valid_methods:
                return {
                    'valid': False,
                    'error': f'Phương thức không hợp lệ: {choice_method}'
                }
            
            # Xác thực risk threshold cho AUTO_PROTECTION
            if choice_method == 'AUTO_PROTECTION':
                if not risk_threshold or risk_threshold <= 0:
                    return {
                        'valid': False,
                        'error': 'AUTO_PROTECTION yêu cầu ngưỡng rủi ro hợp lệ'
                    }
                
                if risk_threshold > 100000:  # Giới hạn $100,000
                    return {
                        'valid': False,
                        'error': 'Ngưỡng rủi ro quá cao (> $100,000)'
                    }
            
            return {
                'valid': True,
                'choice_method': choice_method,
                'risk_threshold': float(risk_threshold) if risk_threshold else None,
                'description': 'Lựa chọn quản lý rủi ro hợp lệ'
            }
            
        except Exception as e:
            self.logger.error(f"Error validating risk management choice: {str(e)}")
            return {'error': f'Validation failed: {str(e)}'}
    
    def _is_system_admin(self, user_id: str) -> bool:
        """Kiểm tra xem user có phải là system admin không"""
        # Trong thực tế, cần query từ user service
        # Đây là logic mẫu để test
        system_admin_ids = ['admin_001', 'super_admin', 'system']
        return user_id in system_admin_ids
    
    def _is_designated_admin(self, user_id: str) -> bool:
        """Kiểm tra xem user có phải là designated admin không"""
        # Trong thực tế, cần query từ user service
        # Đây là logic mẫu để test
        designated_admin_ids = ['admin_002', 'admin_003', 'designated_admin']
        return user_id in designated_admin_ids
    
    def _is_individual_bookmaker(self, user_id: str) -> bool:
        """Kiểm tra xem user có phải là individual bookmaker không"""
        # Trong thực tế, cần query từ user service
        # Đây là logic mẫu để test
        individual_ids = ['user_001', 'user_002', 'individual_bookmaker']
        return user_id in individual_ids
    
    def _is_group_bookmaker(self, user_id: str) -> bool:
        """Kiểm tra xem user có phải là group bookmaker không"""
        # Trong thực tế, cần query từ groups service
        # Đây là logic mẫu để test
        group_ids = ['group_001', 'group_002', 'group_bookmaker']
        return user_id in group_ids
    
    def _get_individual_risk_choice(self, user_id: str, match_id: str) -> Dict:
        """Lấy lựa chọn quản lý rủi ro của individual bookmaker"""
        # Trong thực tế, cần query từ database
        # Đây là dữ liệu mẫu để test
        sample_choices = {
            'user_001': {
                'method': 'AUTO_PROTECTION',
                'method_display': 'Kích hoạt bảo vệ tự động',
                'risk_threshold': 5000.0,
                'is_confirmed': True
            },
            'user_002': {
                'method': 'MANUAL_MANAGEMENT',
                'method_display': 'Tự quản lý rủi ro thủ công',
                'risk_threshold': None,
                'is_confirmed': True
            }
        }
        
        return sample_choices.get(user_id, {
            'method': 'MANUAL_MANAGEMENT',
            'method_display': 'Tự quản lý rủi ro thủ công',
            'risk_threshold': None,
            'is_confirmed': False
        })
    
    def _get_group_risk_choice(self, user_id: str, match_id: str) -> Dict:
        """Lấy lựa chọn quản lý rủi ro của group bookmaker"""
        # Trong thực tế, cần query từ groups service
        # Đây là dữ liệu mẫu để test
        sample_group_choices = {
            'group_001': {
                'method': 'AUTO_PROTECTION',
                'method_display': 'Kích hoạt bảo vệ tự động',
                'risk_threshold': 10000.0,
                'is_confirmed': True
            },
            'group_002': {
                'method': 'MANUAL_MANAGEMENT',
                'method_display': 'Tự quản lý rủi ro thủ công',
                'risk_threshold': None,
                'is_confirmed': True
            }
        }
        
        # Giả sử user thuộc group đầu tiên
        return sample_group_choices.get('group_001', {
            'method': 'MANUAL_MANAGEMENT',
            'method_display': 'Tự quản lý rủi ro thủ công',
            'risk_threshold': None,
            'is_confirmed': False
        })
    
    def _get_existing_risk_choice(self, user_id: str, match_id: str) -> Optional[Dict]:
        """Lấy lựa chọn quản lý rủi ro hiện tại (nếu có)"""
        # Trong thực tế, cần query từ database
        # Đây là logic mẫu để test
        return None  # Giả sử chưa có lựa chọn

class RiskManagementOrchestratorService:
    """Service tổng hợp để điều phối tất cả các service quản lý rủi ro"""
    
    def __init__(self):
        self.logger = logging.getLogger('risk_manager')
        
        # Khởi tạo các service con
        self.liability_calculation_service = LiabilityCalculationService()
        self.vigorish_margin_service = VigorishMarginService()
        self.risk_threshold_service = RiskThresholdService()
        self.promotion_risk_service = PromotionRiskService()
        self.inplay_risk_service = InPlayRiskService()
        self.bookmaker_role_service = BookmakerRoleManagementService()
    
    def comprehensive_risk_assessment(self, match_id: str, user_id: str, bet_data: Dict) -> Dict:
        """
        Đánh giá rủi ro toàn diện cho một bet
        
        Args:
            match_id: ID của trận đấu
            user_id: ID của user đặt cược
            bet_data: Dữ liệu bet
        """
        try:
            # 1. Xác định vai trò nhà cái
            bookmaker_role = self.bookmaker_role_service.determine_bookmaker_role(user_id, match_id)
            
            # 2. Áp dụng quy tắc rủi ro theo vai trò
            risk_rules = self.bookmaker_role_service.apply_risk_rules_by_role(bookmaker_role, bet_data)
            
            # 3. Tính toán Trách Nhiệm RÒNG
            liability_calculation = self.liability_calculation_service.calculate_net_liability(
                match_id, bet_data.get('bet_type_id'), bet_data.get('outcome')
            )
            
            # 4. Kiểm tra ngưỡng rủi ro
            threshold_check = self.risk_threshold_service.check_risk_threshold(
                match_id, bet_data.get('bet_type_id'), bet_data.get('outcome'),
                Decimal(str(bet_data.get('stake_amount', '0')))
            )
            
            # 5. Đánh giá rủi ro promotion (nếu có)
            promotion_risk = None
            if bet_data.get('promotion_type'):
                promotion_risk = self.promotion_risk_service.calculate_promotion_risk(bet_data)
            
            # 6. Tổng hợp kết quả
            comprehensive_result = {
                'match_id': match_id,
                'user_id': user_id,
                'assessment_timestamp': timezone.now().isoformat(),
                'bookmaker_role': bookmaker_role,
                'risk_rules_applied': risk_rules,
                'liability_calculation': liability_calculation,
                'threshold_check': threshold_check,
                'promotion_risk': promotion_risk,
                'overall_risk_level': self._determine_overall_risk_level(
                    liability_calculation, threshold_check, promotion_risk
                ),
                'recommendations': self._generate_comprehensive_recommendations(
                    bookmaker_role, liability_calculation, threshold_check, promotion_risk
                ),
                'final_decision': self._make_final_decision(
                    threshold_check, bookmaker_role, liability_calculation
                )
            }
            
            # 7. Log audit
            self._log_comprehensive_assessment(comprehensive_result)
            
            return comprehensive_result
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive risk assessment: {str(e)}")
            return {'error': f'Comprehensive assessment failed: {str(e)}'}
    
    def setup_match_risk_management(self, match_id: str, bookmaker_type: str, 
                                  main_threshold: Decimal, promotion_threshold: Decimal = None) -> Dict:
        """
        Thiết lập hệ thống quản lý rủi ro cho một match
        
        Args:
            match_id: ID của trận đấu
            bookmaker_type: Loại nhà cái
            main_threshold: Trần Cố Định CHÍNH
            promotion_threshold: Trần Cố Định PHỤ
        """
        try:
            # 1. Thiết lập ngưỡng rủi ro
            threshold_setup = self.risk_threshold_service.set_risk_thresholds(
                match_id, bookmaker_type, main_threshold, promotion_threshold
            )
            
            # 2. Thiết lập margin (nếu là system admin)
            margin_setup = None
            if bookmaker_type == 'SYSTEM':
                # Sử dụng margin mặc định 5%
                margin_setup = {
                    'margin_enabled': True,
                    'default_margin': 0.05,
                    'description': 'System admin - margin mặc định 5%'
                }
            
            # 3. Thiết lập monitoring
            monitoring_setup = self._setup_risk_monitoring(match_id)
            
            return {
                'match_id': match_id,
                'setup_timestamp': timezone.now().isoformat(),
                'threshold_setup': threshold_setup,
                'margin_setup': margin_setup,
                'monitoring_setup': monitoring_setup,
                'status': 'SETUP_COMPLETE'
            }
            
        except Exception as e:
            self.logger.error(f"Error setting up match risk management: {str(e)}")
            return {'error': f'Setup failed: {str(e)}'}
    
    def handle_inplay_event(self, match_id: str, event_type: str, event_data: Dict) -> Dict:
        """
        Xử lý sự kiện trong trận đấu và cập nhật quản lý rủi ro
        
        Args:
            match_id: ID của trận đấu
            event_type: Loại sự kiện
            event_data: Dữ liệu sự kiện
        """
        try:
            # 1. Xử lý sự kiện trong trận
            inplay_result = self.inplay_risk_service.handle_match_event(
                match_id, event_type, event_data
            )
            
            # 2. Cập nhật liability calculation
            updated_liability = self.liability_calculation_service.calculate_net_liability(
                match_id, 'MATCH_RESULT', 'HOME_WIN'  # Giả sử
            )
            
            # 3. Kiểm tra ngưỡng rủi ro sau sự kiện
            threshold_check = self.risk_threshold_service.check_risk_threshold(
                match_id, 'MATCH_RESULT', 'HOME_WIN', Decimal('0')
            )
            
            # 4. Tự động tạm dừng nếu cần
            auto_suspension = None
            if threshold_check.get('threshold_exceeded', False):
                auto_suspension = self.risk_threshold_service.auto_suspend_market(
                    match_id, 'MATCH_RESULT', 'HOME_WIN'
                )
            
            return {
                'event_handled': True,
                'match_id': match_id,
                'event_type': event_type,
                'inplay_result': inplay_result,
                'updated_liability': updated_liability,
                'threshold_check': threshold_check,
                'auto_suspension': auto_suspension,
                'timestamp': timezone.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error handling inplay event: {str(e)}")
            return {'error': f'Inplay event handling failed: {str(e)}'}
    
    def get_risk_dashboard_data(self, match_id: str = None, user_id: str = None) -> Dict:
        """
        Lấy dữ liệu cho dashboard quản lý rủi ro
        
        Args:
            match_id: ID của trận đấu (nếu có)
            user_id: ID của user (nếu có)
        """
        try:
            dashboard_data = {
                'timestamp': timezone.now().isoformat(),
                'overall_risk_status': 'NORMAL',
                'active_matches': [],
                'risk_alerts': [],
                'system_health': 'HEALTHY'
            }
            
            # Lấy dữ liệu cho từng match
            if match_id:
                match_data = self._get_match_risk_data(match_id)
                dashboard_data['match_details'] = match_data
            
            # Lấy dữ liệu cho từng user
            if user_id:
                user_data = self._get_user_risk_data(user_id)
                dashboard_data['user_details'] = user_data
            
            # Lấy thống kê tổng quan
            dashboard_data['statistics'] = self._get_risk_statistics()
            
            return dashboard_data
            
        except Exception as e:
            self.logger.error(f"Error getting risk dashboard data: {str(e)}")
            return {'error': f'Dashboard data failed: {str(e)}'}
    
    def _determine_overall_risk_level(self, liability_calculation: Dict, 
                                    threshold_check: Dict, promotion_risk: Dict) -> str:
        """Xác định mức độ rủi ro tổng thể"""
        try:
            risk_scores = []
            
            # Đánh giá từ liability calculation
            if 'liability_breakdown' in liability_calculation:
                for outcome, data in liability_calculation['liability_breakdown'].items():
                    if 'risk_level' in data:
                        risk_level = data['risk_level']
                        if risk_level == 'CRITICAL':
                            risk_scores.append(4)
                        elif risk_level == 'HIGH':
                            risk_scores.append(3)
                        elif risk_level == 'MEDIUM':
                            risk_scores.append(2)
                        else:
                            risk_scores.append(1)
            
            # Đánh giá từ threshold check
            if threshold_check.get('threshold_exceeded', False):
                risk_scores.append(4)  # CRITICAL
            elif threshold_check.get('utilization_percentage', 0) > 80:
                risk_scores.append(3)  # HIGH
            elif threshold_check.get('utilization_percentage', 0) > 60:
                risk_scores.append(2)  # MEDIUM
            else:
                risk_scores.append(1)  # LOW
            
            # Đánh giá từ promotion risk
            if promotion_risk and 'risk_level' in promotion_risk:
                promo_risk = promotion_risk['risk_level']
                if promo_risk == 'CRITICAL':
                    risk_scores.append(4)
                elif promo_risk == 'HIGH':
                    risk_scores.append(3)
                elif promo_risk == 'MEDIUM':
                    risk_scores.append(2)
                else:
                    risk_scores.append(1)
            
            # Tính điểm trung bình
            if risk_scores:
                avg_score = sum(risk_scores) / len(risk_scores)
                if avg_score >= 3.5:
                    return 'CRITICAL'
                elif avg_score >= 2.5:
                    return 'HIGH'
                elif avg_score >= 1.5:
                    return 'MEDIUM'
                else:
                    return 'LOW'
            else:
                return 'UNKNOWN'
                
        except Exception as e:
            self.logger.error(f"Error determining overall risk level: {str(e)}")
            return 'UNKNOWN'
    
    def _generate_comprehensive_recommendations(self, bookmaker_role: Dict, 
                                             liability_calculation: Dict,
                                             threshold_check: Dict, 
                                             promotion_risk: Dict) -> List[str]:
        """Tạo khuyến nghị toàn diện"""
        recommendations = []
        
        try:
            # Khuyến nghị dựa trên vai trò
            if bookmaker_role.get('role') == 'SYSTEM':
                recommendations.append("✅ System admin - áp dụng quy tắc an toàn tối đa")
            elif bookmaker_role.get('risk_rules') == 'AUTO_PROTECTION':
                recommendations.append("✅ Auto protection - rủi ro được kiểm soát")
            elif bookmaker_role.get('risk_rules') == 'MANUAL_MANAGEMENT':
                recommendations.append("⚠️ Manual management - cần theo dõi liên tục")
            
            # Khuyến nghị dựa trên liability
            if 'liability_breakdown' in liability_calculation:
                for outcome, data in liability_calculation['liability_breakdown'].items():
                    if data.get('risk_level') == 'CRITICAL':
                        recommendations.append(f"🚨 CRITICAL: {outcome} có rủi ro cực cao")
                    elif data.get('risk_level') == 'HIGH':
                        recommendations.append(f"⚠️ HIGH: {outcome} cần chú ý")
            
            # Khuyến nghị dựa trên threshold
            if threshold_check.get('threshold_exceeded', False):
                recommendations.append("🚨 Vượt ngưỡng rủi ro - cần hành động ngay lập tức")
            elif threshold_check.get('utilization_percentage', 0) > 80:
                recommendations.append("⚠️ Gần đạt ngưỡng rủi ro - cần theo dõi chặt chẽ")
            
            # Khuyến nghị dựa trên promotion risk
            if promotion_risk and promotion_risk.get('risk_level') == 'CRITICAL':
                recommendations.append("🚨 Promotion có rủi ro cực cao - cần xem xét lại")
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating recommendations: {str(e)}")
            return ["Không thể tạo khuyến nghị do lỗi hệ thống"]
    
    def _make_final_decision(self, threshold_check: Dict, bookmaker_role: Dict, 
                            liability_calculation: Dict) -> Dict:
        """Đưa ra quyết định cuối cùng"""
        try:
            # Kiểm tra threshold
            if threshold_check.get('threshold_exceeded', False):
                decision = 'REJECTED'
                reason = 'Vượt ngưỡng rủi ro'
            else:
                decision = 'APPROVED'
                reason = 'Trong giới hạn rủi ro cho phép'
            
            # Kiểm tra vai trò nhà cái
            if bookmaker_role.get('role') == 'SYSTEM':
                decision_authority = 'SYSTEM_AUTO'
            else:
                decision_authority = 'USER_DEFINED'
            
            return {
                'decision': decision,
                'reason': reason,
                'decision_authority': decision_authority,
                'timestamp': timezone.now().isoformat(),
                'requires_manual_review': decision == 'REJECTED'
            }
            
        except Exception as e:
            self.logger.error(f"Error making final decision: {str(e)}")
            return {
                'decision': 'ERROR',
                'reason': f'Lỗi hệ thống: {str(e)}',
                'decision_authority': 'SYSTEM_ERROR',
                'timestamp': timezone.now().isoformat(),
                'requires_manual_review': True
            }
    
    def _setup_risk_monitoring(self, match_id: str) -> Dict:
        """Thiết lập monitoring rủi ro cho match"""
        try:
            # Trong thực tế, cần thiết lập các monitor và alert
            monitoring_config = {
                'liability_monitoring': True,
                'odds_volatility_monitoring': True,
                'pattern_detection': True,
                'real_time_alerts': True,
                'auto_suspension': True
            }
            
            return {
                'status': 'MONITORING_ACTIVE',
                'config': monitoring_config,
                'match_id': match_id
            }
            
        except Exception as e:
            self.logger.error(f"Error setting up risk monitoring: {str(e)}")
            return {'error': f'Monitoring setup failed: {str(e)}'}
    
    def _get_match_risk_data(self, match_id: str) -> Dict:
        """Lấy dữ liệu rủi ro cho một match cụ thể"""
        try:
            # Trong thực tế, cần query từ database
            return {
                'match_id': match_id,
                'current_liability': 5000.0,
                'risk_threshold': 10000.0,
                'utilization_percentage': 50.0,
                'status': 'ACTIVE'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting match risk data: {str(e)}")
            return {}
    
    def _get_user_risk_data(self, user_id: str) -> Dict:
        """Lấy dữ liệu rủi ro cho một user cụ thể"""
        try:
            # Trong thực tế, cần query từ database
            return {
                'user_id': user_id,
                'total_exposure': 2000.0,
                'risk_level': 'MEDIUM',
                'active_bets': 5
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user risk data: {str(e)}")
            return {}
    
    def _get_risk_statistics(self) -> Dict:
        """Lấy thống kê rủi ro tổng quan"""
        try:
            # Trong thực tế, cần query từ database
            return {
                'total_matches': 25,
                'active_matches': 15,
                'suspended_matches': 2,
                'total_liability': 150000.0,
                'average_risk_level': 'MEDIUM'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting risk statistics: {str(e)}")
            return {}
    
    def _log_comprehensive_assessment(self, assessment_result: Dict):
        """Log kết quả đánh giá toàn diện"""
        try:
            RiskAuditLog.objects.create(
                action_type='COMPREHENSIVE_ASSESSMENT',
                action_description=f'Comprehensive risk assessment for match {assessment_result.get("match_id")}',
                user_id=assessment_result.get('user_id', 'system'),
                ip_address='127.0.0.1',
                related_object_type='MATCH',
                related_object_id=assessment_result.get('match_id', 'unknown'),
                action_details=assessment_result
            )
        except Exception as e:
            self.logger.error(f"Error logging comprehensive assessment: {str(e)}")


class RiskAdjustedOddsService:
    """
    Service triển khai công thức Risk-Adjusted Offered Odds
    Công thức: Odds_chào_bán = (Odds_lý_thuyết / M) * (1 - (L_ròng / T_cố_định))
    """
    
    def __init__(self):
        self.logger = logging.getLogger('risk_manager')
    
    def calculate_risk_adjusted_odds(self, 
                                   theoretical_odds: Decimal,
                                   margin_factor: Decimal,
                                   net_liability: Decimal,
                                   risk_threshold: Decimal) -> Dict:
        """
        Tính toán tỷ lệ cược chào bán dựa trên rủi ro
        
        Args:
            theoretical_odds: Odds lý thuyết (Odds_lý_thuyết)
            margin_factor: Biên lợi nhuận mong muốn (M) - ví dụ: 1.05
            net_liability: Trách nhiệm ròng hiện tại (L_ròng)
            risk_threshold: Trần cố định rủi ro (T_cố_định)
        
        Returns:
            Dict chứa kết quả tính toán và trạng thái
        """
        try:
            # Kiểm tra tham số đầu vào
            if theoretical_odds <= 0:
                return self._create_error_result("Odds lý thuyết phải > 0")
            
            if margin_factor <= 1.0:
                return self._create_error_result("Biên lợi nhuận phải > 1.0")
            
            if risk_threshold <= 0:
                return self._create_error_result("Trần rủi ro phải > 0")
            
            # Tính toán theo công thức: Odds_chào_bán = (Odds_lý_thuyết / M) * (1 - (L_ròng / T_cố_định))
            
            # Bước 1: Tính (Odds_lý_thuyết / M)
            odds_with_margin = theoretical_odds / margin_factor
            
            # Bước 2: Tính (L_ròng / T_cố_định)
            liability_ratio = net_liability / risk_threshold
            
            # Bước 3: Tính (1 - (L_ròng / T_cố_định))
            risk_adjustment_factor = Decimal('1.0') - liability_ratio
            
            # Bước 4: Tính Odds_chào_bán cuối cùng
            risk_adjusted_odds = odds_with_margin * risk_adjustment_factor
            
            # Kiểm tra điều kiện khóa thị trường
            market_locked = risk_adjusted_odds <= Decimal('1.0')
            
            # Phân tích trạng thái rủi ro
            risk_status = self._analyze_risk_status(net_liability, risk_threshold, liability_ratio)
            
            # Tạo kết quả
            result = {
                'success': True,
                'theoretical_odds': float(theoretical_odds),
                'margin_factor': float(margin_factor),
                'net_liability': float(net_liability),
                'risk_threshold': float(risk_threshold),
                'odds_with_margin': float(odds_with_margin),
                'liability_ratio': float(liability_ratio),
                'risk_adjustment_factor': float(risk_adjustment_factor),
                'risk_adjusted_odds': float(risk_adjusted_odds),
                'market_locked': market_locked,
                'risk_status': risk_status,
                'recommendations': self._generate_recommendations(risk_status, market_locked, liability_ratio)
            }
            
            # Log kết quả
            self.logger.info(f"Risk-adjusted odds calculated: {float(risk_adjusted_odds):.4f}, "
                           f"Market locked: {market_locked}, Risk status: {risk_status}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error calculating risk-adjusted odds: {str(e)}")
            return self._create_error_result(f"Tính toán thất bại: {str(e)}")
    
    def calculate_batch_risk_adjusted_odds(self, odds_configs: List[Dict]) -> Dict:
        """
        Tính toán risk-adjusted odds cho nhiều cấu hình cùng lúc
        
        Args:
            odds_configs: List các dict chứa cấu hình cho từng odds
        
        Returns:
            Dict chứa kết quả cho tất cả cấu hình
        """
        try:
            results = {}
            
            for i, config in enumerate(odds_configs):
                config_id = config.get('id', f'config_{i}')
                
                # Validate cấu hình
                validation_result = self._validate_odds_config(config)
                if not validation_result['valid']:
                    results[config_id] = self._create_error_result(validation_result['error'])
                    continue
                
                # Tính toán risk-adjusted odds
                result = self.calculate_risk_adjusted_odds(
                    theoretical_odds=Decimal(str(config['theoretical_odds'])),
                    margin_factor=Decimal(str(config['margin_factor'])),
                    net_liability=Decimal(str(config['net_liability'])),
                    risk_threshold=Decimal(str(config['risk_threshold']))
                )
                
                results[config_id] = result
            
            # Tổng hợp kết quả
            total_configs = len(odds_configs)
            successful_configs = sum(1 for r in results.values() if r.get('success', False))
            locked_markets = sum(1 for r in results.values() if r.get('market_locked', False))
            
            return {
                'success': True,
                'total_configs': total_configs,
                'successful_configs': successful_configs,
                'failed_configs': total_configs - successful_configs,
                'locked_markets': locked_markets,
                'results': results,
                'summary': {
                    'success_rate': (successful_configs / total_configs) * 100 if total_configs > 0 else 0,
                    'lock_rate': (locked_markets / total_configs) * 100 if total_configs > 0 else 0
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating batch risk-adjusted odds: {str(e)}")
            return self._create_error_result(f"Tính toán batch thất bại: {str(e)}")
    
    def _analyze_risk_status(self, net_liability: Decimal, risk_threshold: Decimal, liability_ratio: float) -> str:
        """Phân tích trạng thái rủi ro"""
        if net_liability < 0:
            return "SAFE"  # An toàn - có lợi nhuận
        elif liability_ratio < 0.5:
            return "LOW_RISK"  # Rủi ro thấp
        elif liability_ratio < 0.8:
            return "MEDIUM_RISK"  # Rủi ro trung bình
        elif liability_ratio < 1.0:
            return "HIGH_RISK"  # Rủi ro cao
        else:
            return "CRITICAL_RISK"  # Rủi ro cực kỳ cao
    
    def _generate_recommendations(self, risk_status: str, market_locked: bool, liability_ratio: float) -> List[str]:
        """Tạo khuyến nghị dựa trên trạng thái rủi ro"""
        recommendations = []
        
        if market_locked:
            recommendations.append("🚫 THỊ TRƯỜNG BỊ KHÓA: Odds ≤ 1.0, cần điều chỉnh ngay lập tức")
        
        if risk_status == "SAFE":
            recommendations.append("✅ An toàn: Có thể tăng odds để thu hút thêm cược")
            recommendations.append("💡 Cân nhắc giảm margin để cạnh tranh tốt hơn")
        elif risk_status == "LOW_RISK":
            recommendations.append("🟢 Rủi ro thấp: Tiếp tục theo dõi")
        elif risk_status == "MEDIUM_RISK":
            recommendations.append("🟡 Rủi ro trung bình: Cần theo dõi chặt chẽ")
            recommendations.append("⚠️ Cân nhắc tăng odds để giảm rủi ro")
        elif risk_status == "HIGH_RISK":
            recommendations.append("🟠 Rủi ro cao: Cần hành động ngay")
            recommendations.append("📈 Tăng odds đáng kể để giảm rủi ro")
            recommendations.append("🔍 Kiểm tra pattern betting bất thường")
        elif risk_status == "CRITICAL_RISK":
            recommendations.append("🔴 RỦI RO CỰC KỲ CAO: Hành động khẩn cấp")
            recommendations.append("🚫 Tạm dừng nhận cược mới")
            recommendations.append("📞 Thông báo ngay cho quản lý")
            recommendations.append("🔍 Phân tích nguyên nhân và xử lý")
        
        # Khuyến nghị dựa trên tỷ lệ liability
        if liability_ratio > 0.9:
            recommendations.append("⚠️ Gần đạt giới hạn rủi ro tối đa")
        elif liability_ratio > 0.7:
            recommendations.append("📊 Rủi ro đang tăng, cần theo dõi")
        
        return recommendations
    
    def _validate_odds_config(self, config: Dict) -> Dict:
        """Validate cấu hình odds"""
        required_fields = ['theoretical_odds', 'margin_factor', 'net_liability', 'risk_threshold']
        
        for field in required_fields:
            if field not in config:
                return {'valid': False, 'error': f'Thiếu trường bắt buộc: {field}'}
        
        try:
            # Kiểm tra giá trị
            if Decimal(str(config['theoretical_odds'])) <= 0:
                return {'valid': False, 'error': 'Odds lý thuyết phải > 0'}
            
            if Decimal(str(config['margin_factor'])) <= 1.0:
                return {'valid': False, 'error': 'Biên lợi nhuận phải > 1.0'}
            
            if Decimal(str(config['risk_threshold'])) <= 0:
                return {'valid': False, 'error': 'Trần rủi ro phải > 0'}
            
            return {'valid': True}
            
        except (ValueError, TypeError) as e:
            return {'valid': False, 'error': f'Giá trị không hợp lệ: {str(e)}'}
    
    def _create_error_result(self, error_message: str) -> Dict:
        """Tạo kết quả lỗi"""
        return {
            'success': False,
            'error': error_message,
            'risk_adjusted_odds': None,
            'market_locked': True
        }
    
    def get_risk_adjustment_explanation(self, 
                                      theoretical_odds: Decimal,
                                      margin_factor: Decimal,
                                      net_liability: Decimal,
                                      risk_threshold: Decimal) -> Dict:
        """
        Giải thích chi tiết quá trình tính toán risk-adjusted odds
        """
        try:
            # Tính từng bước
            odds_with_margin = theoretical_odds / margin_factor
            liability_ratio = net_liability / risk_threshold
            risk_adjustment_factor = Decimal('1.0') - liability_ratio
            final_odds = odds_with_margin * risk_adjustment_factor
            
            explanation = {
                'formula': 'Odds_chào_bán = (Odds_lý_thuyết / M) * (1 - (L_ròng / T_cố_định))',
                'steps': {
                    'step_1': {
                        'description': 'Tính (Odds_lý_thuyết / M)',
                        'calculation': f'{float(theoretical_odds)} / {float(margin_factor)}',
                        'result': float(odds_with_margin),
                        'explanation': f'Áp dụng biên lợi nhuận {float(margin_factor)} để đảm bảo lợi nhuận'
                    },
                    'step_2': {
                        'description': 'Tính (L_ròng / T_cố_định)',
                        'calculation': f'{float(net_liability)} / {float(risk_threshold)}',
                        'result': float(liability_ratio),
                        'explanation': f'Tỷ lệ rủi ro hiện tại: {float(liability_ratio)*100:.2f}%'
                    },
                    'step_3': {
                        'description': 'Tính (1 - (L_ròng / T_cố_định))',
                        'calculation': f'1 - {float(liability_ratio)}',
                        'result': float(risk_adjustment_factor),
                        'explanation': self._get_risk_factor_explanation(risk_adjustment_factor)
                    },
                    'step_4': {
                        'description': 'Tính Odds_chào_bán cuối cùng',
                        'calculation': f'{float(odds_with_margin)} * {float(risk_adjustment_factor)}',
                        'result': float(final_odds),
                        'explanation': 'Kết quả cuối cùng sau khi điều chỉnh rủi ro'
                    }
                },
                'risk_analysis': {
                    'net_liability': float(net_liability),
                    'risk_threshold': float(risk_threshold),
                    'liability_ratio': float(liability_ratio),
                    'risk_status': self._analyze_risk_status(net_liability, risk_threshold, liability_ratio),
                    'market_impact': 'Tăng odds' if risk_adjustment_factor > 1 else 'Giảm odds' if risk_adjustment_factor < 1 else 'Giữ nguyên'
                }
            }
            
            return explanation
            
        except Exception as e:
            return {'error': f'Không thể tạo giải thích: {str(e)}'}
    
    def _get_risk_factor_explanation(self, risk_adjustment_factor: Decimal) -> str:
        """Giải thích ý nghĩa của risk adjustment factor"""
        factor = float(risk_adjustment_factor)
        
        if factor > 1.0:
            return f"Hệ số {factor:.3f} > 1: Rủi ro thấp, tăng odds để thu hút cược"
        elif factor < 1.0:
            return f"Hệ số {factor:.3f} < 1: Rủi ro cao, giảm odds để bảo vệ"
        else:
            return f"Hệ số {factor:.3f} = 1: Rủi ro cân bằng, giữ nguyên odds"
