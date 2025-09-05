import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import json

# ============================================================================
# BETTING SYSTEM RISK MANAGEMENT MODELS - 50+ Sports & 50+ Bet Types
# ============================================================================

# Sport Categories and Names (matching betting system)
SPORT_CATEGORIES = [
    ('BALL_SPORTS', 'Thể thao bóng'),
    ('RACING', 'Thể thao đua'),
    ('COMBAT', 'Thể thao đối kháng'),
    ('INDIVIDUAL', 'Thể thao cá nhân'),
    ('WINTER', 'Thể thao mùa đông'),
    ('WATER', 'Thể thao dưới nước'),
    ('MOTOR', 'Thể thao động cơ'),
    ('SPECIAL', 'Thể thao đặc biệt'),
]

SPORT_NAMES = [
    # BALL_SPORTS
    'Football', 'Basketball', 'Tennis', 'Baseball', 'American Football',
    'Ice Hockey', 'Volleyball', 'Table Tennis', 'Badminton', 'Beach Volleyball',
    'Futsal', 'Gaelic Football', 'Handball', 'Netball', 'Water Polo',
    # RACING
    'Horse Racing', 'Australasian Racing', 'Trotting', 'Cycling', 'Formula 1',
    'Motor Racing', 'Motorbikes', 'Speedway', 'Rowing', 'Yachting',
    # COMBAT
    'Boxing', 'MMA', 'Cricket', 'Rugby League', 'Rugby Union', 'Kabaddi', 'Lacrosse',
    # INDIVIDUAL
    'Golf', 'Chess', 'Snooker & Pool', 'Darts', 'Bowls',
    # WINTER
    'Winter Sports',
    # WATER
    'Swimming', 'Surfing',
    # MOTOR
    'Esports',
    # SPECIAL
    'Athletics', 'Australian Rules', 'Bandy', 'Floorball', 'International Rules', 'Special Markets'
]

BET_TYPE_CATEGORIES = [
    ('MATCH_RESULT', 'Kết quả trận đấu'),
    ('SCORING', 'Ghi bàn/điểm'),
    ('PERFORMANCE', 'Hiệu suất'),
    ('SPECIAL_EVENTS', 'Sự kiện đặc biệt'),
    ('COMBINATIONS', 'Kết hợp'),
    ('FUTURES', 'Tương lai'),
    ('LIVE_BETTING', 'Cược trực tiếp'),
    ('SPECIAL_MARKETS', 'Thị trường đặc biệt'),
]

BET_TYPE_NAMES = [
    # MATCH_RESULT
    'Moneyline', 'Point Spread', 'Totals', 'Handicap', 'Asian Handicap',
    'Over/Under', 'Half-Time/Full-Time', 'Correct Score', 'Double Chance',
    # SCORING
    'First Goal Scorer', 'Last Goal Scorer', 'Top Batsman', 'Top Bowler',
    'Man of the Match', 'Total Goals', 'Total Points', 'Total Sets',
    # PERFORMANCE
    'Player Props', 'Team Performance', 'Individual Performance',
    'Shots on Target', 'Corners', 'Cards', 'Fouls',
    # SPECIAL_EVENTS
    'Cược Phạt Góc', 'Cược Thẻ Phạt', 'Cược Hiệp/Nửa trận',
    'Đội Đạt X Điểm Trước', 'Biên Độ Chiến Thắng',
    # COMBINATIONS
    'Forecast/Exacta', 'Tricast/Trifecta', 'Each-Way',
    'Set Betting', 'Round Betting', 'Period Betting',
    # FUTURES
    'Tournament Winner', 'Season Winner', 'Championship Winner',
    'League Position', 'Relegation', 'Promotion',
    # LIVE_BETTING
    'Next Goal', 'Next Point', 'Next Set', 'Next Round',
    'Live Handicap', 'Live Totals',
    # SPECIAL_MARKETS
    'Method of Victory', 'Fight to Go the Distance', 'Race Winner',
    'Podium Finish', 'Head-to-Head', 'To Make/Miss the Cut',
    'Map Winner', 'Cược Kèo Đặc Thù Game', 'Cầu Thủ Xuất Sắc Nhất',
    'Frame Handicap', 'Highest Break', 'Highest Checkout'
]

class PriceVolatilityMonitor(models.Model):
    """Model theo dõi biến động giá trong P2P Marketplace"""
    
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Thông tin phiếu cược
    bet_slip_id = models.CharField(max_length=255, help_text='ID của phiếu cược')
    market_identifier = models.CharField(max_length=255, help_text='Định danh thị trường')
    
    # Giá cả
    original_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Giá gốc')
    current_price = models.DecimalField(max_digits=10, decimal_places=2, help_text='Giá hiện tại')
    price_change_percentage = models.DecimalField(max_digits=5, decimal_places=2, help_text='% thay đổi giá')
    
    # Thông tin biến động
    volatility_score = models.DecimalField(max_digits=5, decimal_places=2, help_text='Điểm số biến động')
    severity_level = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    
    # Metadata
    detection_time = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True, null=True)
    
    # Thông tin bổ sung
    metadata = models.JSONField(default=dict, help_text='Thông tin bổ sung')
    
    class Meta:
        db_table = 'risk_price_volatility_monitor'
        indexes = [
            models.Index(fields=['detection_time']),
            models.Index(fields=['severity_level']),
            models.Index(fields=['bet_slip_id']),
        ]
    
    def __str__(self):
        return f"Price Volatility - {self.bet_slip_id}: {self.price_change_percentage}%"

class MarketActivityMonitor(models.Model):
    """Model theo dõi hoạt động thị trường P2P"""
    
    ACTIVITY_TYPES = [
        ('UNUSUAL_VOLUME', 'Unusual Volume'),
        ('RAPID_PRICE_CHANGE', 'Rapid Price Change'),
        ('SUSPICIOUS_PATTERN', 'Suspicious Pattern'),
        ('HIGH_FREQUENCY_TRADING', 'High Frequency Trading'),
        ('LARGE_ORDER', 'Large Order'),
        ('MARKET_MANIPULATION', 'Market Manipulation'),
    ]
    
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Thông tin hoạt động
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    market_identifier = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255, help_text='ID người dùng liên quan')
    
    # Chi tiết hoạt động
    description = models.TextField()
    severity_level = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, help_text='Độ tin cậy (0.00-1.00)')
    
    # Dữ liệu liên quan
    related_orders = models.JSONField(default=list, help_text='Danh sách lệnh liên quan')
    volume_data = models.JSONField(default=dict, help_text='Dữ liệu volume')
    price_data = models.JSONField(default=dict, help_text='Dữ liệu giá')
    
    # Metadata
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.CharField(max_length=255, blank=True, null=True)
    resolution_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'risk_market_activity_monitor'
        indexes = [
            models.Index(fields=['detected_at']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['severity_level']),
            models.Index(fields=['user_id']),
        ]
    
    def __str__(self):
        return f"Market Activity - {self.activity_type}: {self.market_identifier}"

class TradingSuspension(models.Model):
    """Model quản lý tạm dừng giao dịch"""
    
    SUSPENSION_TYPES = [
        ('SPORT_SPECIFIC', 'Sport Specific'),
        ('MARKET_SPECIFIC', 'Market Specific'),
        ('USER_SPECIFIC', 'User Specific'),
        ('GLOBAL', 'Global'),
        ('EVENT_SPECIFIC', 'Event Specific'),
    ]
    
    SUSPENSION_REASONS = [
        ('PRICE_VOLATILITY', 'Price Volatility'),
        ('SUSPICIOUS_ACTIVITY', 'Suspicious Activity'),
        ('TECHNICAL_ISSUE', 'Technical Issue'),
        ('MANUAL_INTERVENTION', 'Manual Intervention'),
        ('REGULATORY_COMPLIANCE', 'Regulatory Compliance'),
        ('RISK_MANAGEMENT', 'Risk Management'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('LIFTED', 'Lifted'),
        ('EXPIRED', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Thông tin tạm dừng
    suspension_type = models.CharField(max_length=50, choices=SUSPENSION_TYPES)
    reason = models.CharField(max_length=50, choices=SUSPENSION_REASONS)
    description = models.TextField()
    
    # Phạm vi tạm dừng
    sport_id = models.CharField(max_length=255, blank=True, null=True)
    market_identifier = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    event_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Thời gian
    suspended_at = models.DateTimeField(auto_now_add=True)
    suspended_by = models.CharField(max_length=255)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    lifted_at = models.DateTimeField(null=True, blank=True)
    lifted_by = models.CharField(max_length=255, blank=True, null=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'risk_trading_suspension'
        indexes = [
            models.Index(fields=['suspended_at']),
            models.Index(fields=['status']),
            models.Index(fields=['suspension_type']),
            models.Index(fields=['sport_id']),
            models.Index(fields=['user_id']),
        ]
    
    def __str__(self):
        return f"Suspension - {self.suspension_type}: {self.reason}"
    
    def lift_suspension(self, lifted_by):
        """Dỡ bỏ tạm dừng"""
        self.status = 'LIFTED'
        self.lifted_at = timezone.now()
        self.lifted_by = lifted_by
        self.save()

class RiskConfiguration(models.Model):
    """Model cấu hình tham số rủi ro"""
    
    CONFIG_TYPES = [
        ('PRICE_VOLATILITY', 'Price Volatility'),
        ('VOLUME_THRESHOLD', 'Volume Threshold'),
        ('USER_LIMITS', 'User Limits'),
        ('MARKET_LIMITS', 'Market Limits'),
        ('ALERT_SETTINGS', 'Alert Settings'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Thông tin cấu hình
    config_type = models.CharField(max_length=50, choices=CONFIG_TYPES)
    config_key = models.CharField(max_length=255, unique=True)
    config_value = models.JSONField(help_text='Giá trị cấu hình')
    
    # Metadata
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'risk_configuration'
        indexes = [
            models.Index(fields=['config_type']),
            models.Index(fields=['config_key']),
        ]
    
    def __str__(self):
        return f"Risk Config - {self.config_key}"

class RiskAlert(models.Model):
    """Model cảnh báo rủi ro"""
    
    ALERT_TYPES = [
        ('PRICE_VOLATILITY', 'Price Volatility'),
        ('UNUSUAL_ACTIVITY', 'Unusual Activity'),
        ('TRADING_SUSPENSION', 'Trading Suspension'),
        ('SYSTEM_ANOMALY', 'System Anomaly'),
        ('COMPLIANCE_ISSUE', 'Compliance Issue'),
    ]
    
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('ACKNOWLEDGED', 'Acknowledged'),
        ('RESOLVED', 'Resolved'),
        ('DISMISSED', 'Dismissed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Thông tin cảnh báo
    alert_type = models.CharField(max_length=50, choices=ALERT_TYPES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    # Dữ liệu liên quan
    related_data = models.JSONField(default=dict)
    affected_users = models.JSONField(default=list)
    affected_markets = models.JSONField(default=list)
    
    # Status và metadata
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.CharField(max_length=255, blank=True, null=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.CharField(max_length=255, blank=True, null=True)
    resolution_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'risk_alert'
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['alert_type']),
            models.Index(fields=['severity']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Alert - {self.alert_type}: {self.title}"
    
    def acknowledge(self, acknowledged_by):
        """Xác nhận cảnh báo"""
        self.status = 'ACKNOWLEDGED'
        self.acknowledged_at = timezone.now()
        self.acknowledged_by = acknowledged_by
        self.save()
    
    def resolve(self, resolved_by, resolution_notes=""):
        """Giải quyết cảnh báo"""
        self.status = 'RESOLVED'
        self.resolved_at = timezone.now()
        self.resolved_by = resolved_by
        self.resolution_notes = resolution_notes
        self.save()

class RiskMetrics(models.Model):
    """Model lưu trữ metrics rủi ro theo thời gian"""
    
    METRIC_TYPES = [
        ('DAILY_VOLUME', 'Daily Volume'),
        ('PRICE_VOLATILITY', 'Price Volatility'),
        ('USER_ACTIVITY', 'User Activity'),
        ('MARKET_HEALTH', 'Market Health'),
        ('SYSTEM_PERFORMANCE', 'System Performance'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Thông tin metrics
    metric_type = models.CharField(max_length=50, choices=METRIC_TYPES)
    metric_name = models.CharField(max_length=255)
    metric_value = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Phạm vi
    sport_id = models.CharField(max_length=255, blank=True, null=True)
    market_identifier = models.CharField(max_length=255, blank=True, null=True)
    
    # Thời gian
    timestamp = models.DateTimeField(auto_now_add=True)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    
    # Metadata
    metadata = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'risk_metrics'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['metric_type']),
            models.Index(fields=['sport_id']),
            models.Index(fields=['period_start', 'period_end']),
        ]
    
    def __str__(self):
        return f"Metrics - {self.metric_name}: {self.metric_value}"

class RiskAuditLog(models.Model):
    """Model audit log cho risk management"""
    
    ACTION_TYPES = [
        ('SUSPENSION_CREATED', 'Suspension Created'),
        ('SUSPENSION_LIFTED', 'Suspension Lifted'),
        ('ALERT_CREATED', 'Alert Created'),
        ('ALERT_RESOLVED', 'Alert Resolved'),
        ('CONFIG_UPDATED', 'Configuration Updated'),
        ('MANUAL_INTERVENTION', 'Manual Intervention'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Thông tin action
    action_type = models.CharField(max_length=50, choices=ACTION_TYPES)
    action_description = models.TextField()
    
    # User và IP
    user_id = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)
    
    # Dữ liệu liên quan
    related_object_type = models.CharField(max_length=255, blank=True, null=True)
    related_object_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Details
    action_details = models.JSONField(default=dict)
    
    # Metadata
    timestamp = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=True)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'risk_audit_log'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['action_type']),
            models.Index(fields=['user_id']),
        ]
    
    def __str__(self):
        return f"Risk Audit - {self.action_type}: {self.user_id}"

# ============================================================================
# LEGACY MODELS (Giữ lại để tương thích)
# ============================================================================

class RiskProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='risk_profile')
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    risk_level = models.CharField(max_length=50, default='low') # low, medium, high, critical
    max_bet_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    max_daily_loss = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_monitored = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Risk Profile for {self.user.username}"

class RiskSetting(models.Model):
    name = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class PayoutLiability(models.Model):
    match = models.ForeignKey('betting.Match', on_delete=models.CASCADE, related_name='payout_liabilities')
    bet_type = models.ForeignKey('betting.BetType', on_delete=models.CASCADE, related_name='payout_liabilities')
    outcome = models.CharField(max_length=100)
    total_stake = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    potential_payout = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("match", "bet_type", "outcome")

    def __str__(self):
        return f"Liability for {self.match} - {self.bet_type.name} ({self.outcome})"

class OddsAdjustment(models.Model):
    odd = models.ForeignKey('betting.Odd', on_delete=models.CASCADE, related_name='adjustments')
    old_value = models.DecimalField(max_digits=5, decimal_places=2)
    new_value = models.DecimalField(max_digits=5, decimal_places=2)
    adjusted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Odd {self.odd.id} adjusted from {self.old_value} to {self.new_value}"

class PromotionImpact(models.Model):
    promotion = models.ForeignKey('promotions.Promotion', on_delete=models.CASCADE, related_name='impacts')
    match = models.ForeignKey('betting.Match', on_delete=models.CASCADE, related_name='promotion_impacts', blank=True, null=True)
    total_bonus_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0.0)
    total_bets_placed = models.IntegerField(default=0)
    impact_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Impact of {self.promotion.name} on {self.match.id if self.match else 'overall'}"

class RiskLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=100)
    description = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    related_object_id = models.CharField(max_length=255, blank=True, null=True)
    related_object_type = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"[{self.timestamp}] {self.event_type}: {self.description}"

# ============================================================================
# BETTING SYSTEM SPECIFIC RISK MODELS
# ============================================================================

class SportRiskConfiguration(models.Model):
    """Risk configuration cho từng môn thể thao"""
    
    RISK_LEVELS = [
        ('LOW', 'Low Risk'),
        ('MEDIUM', 'Medium Risk'),
        ('HIGH', 'High Risk'),
        ('CRITICAL', 'Critical Risk'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Sport information
    sport_id = models.IntegerField(help_text='ID môn thể thao từ betting service')
    sport_name = models.CharField(max_length=100, choices=[(name, name) for name in SPORT_NAMES])
    sport_category = models.CharField(max_length=50, choices=SPORT_CATEGORIES)
    
    # Risk configuration
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='LOW')
    max_daily_volume = models.DecimalField(max_digits=15, decimal_places=2, 
                                         help_text='Khối lượng cược tối đa mỗi ngày')
    max_single_bet = models.DecimalField(max_digits=12, decimal_places=2,
                                       help_text='Mức cược đơn tối đa')
    max_odds_value = models.DecimalField(max_digits=8, decimal_places=2, default=1000.00,
                                       help_text='Tỷ lệ cược tối đa cho phép')
    min_odds_value = models.DecimalField(max_digits=5, decimal_places=2, default=1.01,
                                       help_text='Tỷ lệ cược tối thiểu')
    
    # Volatility settings
    max_odds_change_percent = models.DecimalField(max_digits=5, decimal_places=2, default=50.00,
                                                help_text='% thay đổi tỷ lệ tối đa trong 1 phút')
    volatility_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=25.00,
                                             help_text='Ngưỡng biến động cảnh báo')
    
    # Trading controls
    auto_suspend_enabled = models.BooleanField(default=True,
                                             help_text='Tự động tạm dừng khi vượt ngưỡng')
    suspension_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=75.00,
                                             help_text='Ngưỡng tự động tạm dừng')
    
    # Liability limits
    max_liability_per_match = models.DecimalField(max_digits=15, decimal_places=2,
                                                help_text='Tổng liability tối đa trên 1 trận')
    max_liability_per_outcome = models.DecimalField(max_digits=15, decimal_places=2,
                                                  help_text='Liability tối đa trên 1 kết quả')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_trading_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True, null=True)
    suspended_at = models.DateTimeField(null=True, blank=True)
    suspended_by = models.CharField(max_length=255, blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=255, help_text='User ID who updated')
    
    class Meta:
        db_table = 'risk_sport_configuration'
        unique_together = ('sport_id', 'sport_name')
        indexes = [
            models.Index(fields=['sport_category']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['is_trading_suspended']),
            models.Index(fields=['updated_at']),
        ]
    
    def __str__(self):
        return f"Sport Risk Config - {self.sport_name} ({self.risk_level})"
    
    def suspend_trading(self, reason, suspended_by):
        """Tạm dừng trading cho sport này"""
        self.is_trading_suspended = True
        self.suspension_reason = reason
        self.suspended_at = timezone.now()
        self.suspended_by = suspended_by
        self.save()
    
    def resume_trading(self, resumed_by):
        """Khôi phục trading cho sport này"""
        self.is_trading_suspended = False
        self.suspension_reason = None
        self.suspended_at = None
        self.suspended_by = None
        self.save()

class BetTypeRiskConfiguration(models.Model):
    """Risk configuration cho từng loại cược"""
    
    RISK_LEVELS = [
        ('LOW', 'Low Risk'),
        ('MEDIUM', 'Medium Risk'),
        ('HIGH', 'High Risk'),
        ('CRITICAL', 'Critical Risk'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Bet type information
    bet_type_id = models.IntegerField(help_text='ID loại cược từ betting service')
    bet_type_name = models.CharField(max_length=100, choices=[(name, name) for name in BET_TYPE_NAMES])
    bet_type_category = models.CharField(max_length=50, choices=BET_TYPE_CATEGORIES)
    sport_name = models.CharField(max_length=100, choices=[(name, name) for name in SPORT_NAMES])
    
    # Risk settings
    risk_level = models.CharField(max_length=20, choices=RISK_LEVELS, default='LOW')
    max_stake_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.00,
                                             help_text='Hệ số nhân stake tối đa so với base')
    max_odds_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.00,
                                            help_text='Hệ số nhân odds tối đa so với base')
    
    # Liability controls
    max_liability_per_bet = models.DecimalField(max_digits=12, decimal_places=2,
                                              help_text='Liability tối đa trên 1 bet')
    max_total_liability = models.DecimalField(max_digits=15, decimal_places=2,
                                            help_text='Tổng liability tối đa cho bet type này')
    
    # Auto adjustment
    auto_adjust_enabled = models.BooleanField(default=True,
                                            help_text='Tự động điều chỉnh odds theo liability')
    adjustment_trigger_percent = models.DecimalField(max_digits=5, decimal_places=2, default=80.00,
                                                   help_text='% liability kích hoạt điều chỉnh')
    adjustment_step = models.DecimalField(max_digits=4, decimal_places=3, default=0.05,
                                        help_text='Bước điều chỉnh odds')
    
    # Status
    is_active = models.BooleanField(default=True)
    is_suspended = models.BooleanField(default=False)
    suspension_reason = models.TextField(blank=True, null=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.CharField(max_length=255)
    
    class Meta:
        db_table = 'risk_bet_type_configuration'
        unique_together = ('bet_type_id', 'bet_type_name', 'sport_name')
        indexes = [
            models.Index(fields=['bet_type_category']),
            models.Index(fields=['sport_name']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['is_suspended']),
        ]
    
    def __str__(self):
        return f"BetType Risk Config - {self.bet_type_name} ({self.sport_name})"

class LiveRiskMonitor(models.Model):
    """Monitor rủi ro real-time cho matches và odds"""
    
    MONITOR_TYPES = [
        ('MATCH_VOLUME', 'Match Volume Monitor'),
        ('ODDS_MOVEMENT', 'Odds Movement Monitor'),
        ('LIABILITY_EXPOSURE', 'Liability Exposure Monitor'),
        ('SUSPICIOUS_PATTERN', 'Suspicious Betting Pattern'),
        ('RAPID_STAKE_INCREASE', 'Rapid Stake Increase'),
    ]
    
    STATUS_CHOICES = [
        ('ACTIVE', 'Active Monitoring'),
        ('TRIGGERED', 'Alert Triggered'),
        ('RESOLVED', 'Issue Resolved'),
        ('SUSPENDED', 'Monitoring Suspended'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Monitor details
    monitor_type = models.CharField(max_length=50, choices=MONITOR_TYPES)
    match_id = models.IntegerField(help_text='ID trận đấu từ betting service')
    sport_name = models.CharField(max_length=100, choices=[(name, name) for name in SPORT_NAMES])
    bet_type_id = models.IntegerField(null=True, blank=True, help_text='ID loại cược (nếu có)')
    
    # Current values
    current_value = models.DecimalField(max_digits=15, decimal_places=2,
                                      help_text='Giá trị hiện tại được monitor')
    threshold_value = models.DecimalField(max_digits=15, decimal_places=2,
                                        help_text='Ngưỡng cảnh báo')
    previous_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                       help_text='Giá trị trước đó')
    
    # Risk assessment
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                   help_text='Điểm rủi ro từ 0-100')
    confidence_level = models.DecimalField(max_digits=3, decimal_places=2, default=0.00,
                                         help_text='Độ tin cậy từ 0.00-1.00')
    
    # Status and timing
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    first_detected = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Additional data
    detection_details = models.JSONField(default=dict, help_text='Chi tiết phát hiện')
    action_taken = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'risk_live_monitor'
        indexes = [
            models.Index(fields=['match_id']),
            models.Index(fields=['monitor_type']),
            models.Index(fields=['status']),
            models.Index(fields=['sport_name']),
            models.Index(fields=['first_detected']),
        ]
    
    def __str__(self):
        return f"Live Monitor - {self.monitor_type}: Match {self.match_id}"
    
    def trigger_alert(self, details):
        """Kích hoạt cảnh báo"""
        self.status = 'TRIGGERED'
        self.detection_details.update(details)
        self.save()
    
    def resolve(self, action_taken):
        """Giải quyết vấn đề"""
        self.status = 'RESOLVED'
        self.resolved_at = timezone.now()
        self.action_taken = action_taken
        self.save()

class OddsVolatilityLog(models.Model):
    """Log biến động odds cho analysis"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Odds information
    odds_id = models.IntegerField(help_text='ID odds từ betting service')
    match_id = models.IntegerField(help_text='ID trận đấu')
    bet_type_id = models.IntegerField(help_text='ID loại cược')
    sport_name = models.CharField(max_length=100, choices=[(name, name) for name in SPORT_NAMES])
    outcome = models.CharField(max_length=100, help_text='Kết quả cược (Home Win, etc.)')
    
    # Odds changes
    old_value = models.DecimalField(max_digits=8, decimal_places=2)
    new_value = models.DecimalField(max_digits=8, decimal_places=2)
    change_percentage = models.DecimalField(max_digits=6, decimal_places=2,
                                          help_text='% thay đổi')
    change_reason = models.CharField(max_length=100, choices=[
        ('MARKET_MOVEMENT', 'Market Movement'),
        ('LIABILITY_CONTROL', 'Liability Control'),
        ('MANUAL_ADJUSTMENT', 'Manual Adjustment'),
        ('RISK_MANAGEMENT', 'Risk Management'),
        ('SUSPENSION_RESUME', 'Suspension/Resume'),
        ('SYSTEM_AUTO', 'System Auto Adjustment'),
    ], default='MARKET_MOVEMENT')
    
    # Context
    total_liability_before = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    total_liability_after = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    stakes_count = models.IntegerField(default=0, help_text='Số lượng cược hiện tại')
    
    # Risk assessment
    volatility_score = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    risk_impact = models.CharField(max_length=20, choices=[
        ('LOW', 'Low Impact'),
        ('MEDIUM', 'Medium Impact'),
        ('HIGH', 'High Impact'),
        ('CRITICAL', 'Critical Impact'),
    ], default='LOW')
    
    # Timing
    timestamp = models.DateTimeField(auto_now_add=True)
    adjusted_by = models.CharField(max_length=255, help_text='User/System ID')
    
    # Metadata
    metadata = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'risk_odds_volatility_log'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['match_id']),
            models.Index(fields=['sport_name']),
            models.Index(fields=['change_reason']),
            models.Index(fields=['risk_impact']),
        ]
    
    def __str__(self):
        return f"Odds Volatility - {self.sport_name}: {self.old_value} → {self.new_value}"

class LiabilityExposure(models.Model):
    """Theo dõi exposure liability theo real-time"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Scope information
    match_id = models.IntegerField(help_text='ID trận đấu')
    sport_name = models.CharField(max_length=100, choices=[(name, name) for name in SPORT_NAMES])
    bet_type_id = models.IntegerField(help_text='ID loại cược')
    outcome = models.CharField(max_length=100, help_text='Kết quả cược')
    
    # Exposure data
    current_stake = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                      help_text='Tổng stake hiện tại')
    potential_payout = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                         help_text='Tổng potential payout')
    net_exposure = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                     help_text='Net exposure (payout - stake)')
    
    # Risk metrics
    exposure_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00,
                                            help_text='% exposure so với limit')
    risk_rating = models.CharField(max_length=20, choices=[
        ('LOW', 'Low Risk - < 25%'),
        ('MEDIUM', 'Medium Risk - 25-50%'),
        ('HIGH', 'High Risk - 50-75%'),
        ('CRITICAL', 'Critical Risk - > 75%'),
    ], default='LOW')
    
    # Limits and thresholds
    exposure_limit = models.DecimalField(max_digits=15, decimal_places=2,
                                       help_text='Giới hạn exposure cho outcome này')
    auto_adjust_threshold = models.DecimalField(max_digits=5, decimal_places=2, default=80.00,
                                              help_text='% kích hoạt auto adjust')
    
    # Action flags
    auto_adjust_triggered = models.BooleanField(default=False)
    manual_review_required = models.BooleanField(default=False)
    trading_suspended = models.BooleanField(default=False)
    
    # Timing
    calculated_at = models.DateTimeField(auto_now=True)
    last_bet_time = models.DateTimeField(help_text='Thời gian bet cuối cùng')
    
    # Additional data
    bets_count = models.IntegerField(default=0)
    unique_users_count = models.IntegerField(default=0)
    calculation_metadata = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'risk_liability_exposure'
        unique_together = ('match_id', 'bet_type_id', 'outcome')
        indexes = [
            models.Index(fields=['match_id']),
            models.Index(fields=['sport_name']),
            models.Index(fields=['risk_rating']),
            models.Index(fields=['calculated_at']),
            models.Index(fields=['auto_adjust_triggered']),
        ]
    
    def __str__(self):
        return f"Liability Exposure - {self.sport_name}: {self.net_exposure}"
    
    def update_risk_rating(self):
        """Cập nhật risk rating dựa trên exposure percentage"""
        if self.exposure_percentage < 25:
            self.risk_rating = 'LOW'
        elif self.exposure_percentage < 50:
            self.risk_rating = 'MEDIUM'
        elif self.exposure_percentage < 75:
            self.risk_rating = 'HIGH'
        else:
            self.risk_rating = 'CRITICAL'
        self.save()
    
    def trigger_auto_adjust(self):
        """Kích hoạt auto adjustment"""
        self.auto_adjust_triggered = True
        if self.exposure_percentage > 90:
            self.manual_review_required = True
        self.save()

class BettingPatternAnalysis(models.Model):
    """Phân tích pattern cược để phát hiện bất thường"""
    
    PATTERN_TYPES = [
        ('UNUSUAL_VOLUME', 'Unusual Volume Pattern'),
        ('ODDS_MANIPULATION', 'Odds Manipulation Pattern'),
        ('COORDINATED_BETTING', 'Coordinated Betting Pattern'),
        ('LATE_HEAVY_BETTING', 'Late Heavy Betting Pattern'),
        ('ARBITRAGE_ATTEMPT', 'Arbitrage Attempt Pattern'),
        ('MONEY_LAUNDERING', 'Money Laundering Pattern'),
    ]
    
    SEVERITY_LEVELS = [
        ('LOW', 'Low Concern'),
        ('MEDIUM', 'Medium Concern'),
        ('HIGH', 'High Concern'),
        ('CRITICAL', 'Critical - Immediate Action Required'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Pattern identification
    pattern_type = models.CharField(max_length=50, choices=PATTERN_TYPES)
    severity_level = models.CharField(max_length=20, choices=SEVERITY_LEVELS)
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2,
                                         help_text='Độ tin cậy phát hiện (0.00-1.00)')
    
    # Scope
    match_ids = models.JSONField(default=list, help_text='Danh sách match IDs liên quan')
    sport_names = models.JSONField(default=list, help_text='Danh sách sports liên quan')
    user_ids = models.JSONField(default=list, help_text='Danh sách user IDs liên quan')
    bet_type_ids = models.JSONField(default=list, help_text='Danh sách bet type IDs')
    
    # Pattern details
    pattern_description = models.TextField()
    detection_criteria = models.JSONField(default=dict,
                                        help_text='Tiêu chí phát hiện pattern')
    supporting_evidence = models.JSONField(default=dict,
                                         help_text='Bằng chứng hỗ trợ')
    
    # Financial impact
    total_stake_involved = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    potential_loss_exposure = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    # Detection timing
    pattern_start_time = models.DateTimeField(help_text='Thời gian bắt đầu pattern')
    pattern_end_time = models.DateTimeField(null=True, blank=True)
    detected_at = models.DateTimeField(auto_now_add=True)
    
    # Investigation status
    investigation_status = models.CharField(max_length=30, choices=[
        ('PENDING', 'Pending Investigation'),
        ('INVESTIGATING', 'Under Investigation'),
        ('CONFIRMED', 'Pattern Confirmed'),
        ('FALSE_POSITIVE', 'False Positive'),
        ('RESOLVED', 'Resolved'),
    ], default='PENDING')
    
    investigated_by = models.CharField(max_length=255, blank=True, null=True)
    investigation_notes = models.TextField(blank=True, null=True)
    resolution_action = models.TextField(blank=True, null=True)
    
    # Metadata
    metadata = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'risk_betting_pattern_analysis'
        indexes = [
            models.Index(fields=['detected_at']),
            models.Index(fields=['pattern_type']),
            models.Index(fields=['severity_level']),
            models.Index(fields=['investigation_status']),
        ]
    
    def __str__(self):
        return f"Betting Pattern - {self.pattern_type} ({self.severity_level})"
    
    def start_investigation(self, investigator_id):
        """Bắt đầu điều tra"""
        self.investigation_status = 'INVESTIGATING'
        self.investigated_by = investigator_id
        self.save()
    
    def confirm_pattern(self, action_taken):
        """Xác nhận pattern và hành động"""
        self.investigation_status = 'CONFIRMED'
        self.resolution_action = action_taken
        self.save()
    
    def mark_false_positive(self, reason):
        """Đánh dấu là false positive"""
        self.investigation_status = 'FALSE_POSITIVE'
        self.investigation_notes = reason
        self.save()