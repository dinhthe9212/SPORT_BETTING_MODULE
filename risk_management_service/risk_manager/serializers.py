from rest_framework import serializers
from .models import (
    PriceVolatilityMonitor, MarketActivityMonitor, TradingSuspension,
    RiskConfiguration, RiskAlert, RiskMetrics, RiskAuditLog,
    RiskProfile, RiskSetting, PayoutLiability, OddsAdjustment,
    PromotionImpact, RiskLog
)

# ============================================================================
# P2P MARKETPLACE RISK MANAGEMENT SERIALIZERS
# ============================================================================

class PriceVolatilityMonitorSerializer(serializers.ModelSerializer):
    """Serializer cho Price Volatility Monitor"""
    
    class Meta:
        model = PriceVolatilityMonitor
        fields = '__all__'
        read_only_fields = ('id', 'detection_time', 'volatility_score')

class MarketActivityMonitorSerializer(serializers.ModelSerializer):
    """Serializer cho Market Activity Monitor"""
    
    class Meta:
        model = MarketActivityMonitor
        fields = '__all__'
        read_only_fields = ('id', 'detected_at')

class TradingSuspensionSerializer(serializers.ModelSerializer):
    """Serializer cho Trading Suspension"""
    
    class Meta:
        model = TradingSuspension
        fields = '__all__'
        read_only_fields = ('id', 'suspended_at', 'lifted_at')

class RiskConfigurationSerializer(serializers.ModelSerializer):
    """Serializer cho Risk Configuration"""
    
    class Meta:
        model = RiskConfiguration
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

class RiskAlertSerializer(serializers.ModelSerializer):
    """Serializer cho Risk Alert"""
    
    class Meta:
        model = RiskAlert
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'acknowledged_at', 'resolved_at')

class RiskMetricsSerializer(serializers.ModelSerializer):
    """Serializer cho Risk Metrics"""
    
    class Meta:
        model = RiskMetrics
        fields = '__all__'
        read_only_fields = ('id', 'timestamp')

class RiskAuditLogSerializer(serializers.ModelSerializer):
    """Serializer cho Risk Audit Log"""
    
    class Meta:
        model = RiskAuditLog
        fields = '__all__'
        read_only_fields = ('id', 'timestamp')

# ============================================================================
# REQUEST/RESPONSE SERIALIZERS
# ============================================================================

class PriceVolatilityCheckSerializer(serializers.Serializer):
    """Serializer cho request kiểm tra biến động giá"""
    bet_slip_id = serializers.CharField(max_length=255)
    market_identifier = serializers.CharField(max_length=255)
    original_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    current_price = serializers.DecimalField(max_digits=10, decimal_places=2)

class TradingSuspensionCreateSerializer(serializers.Serializer):
    """Serializer cho request tạo tạm dừng giao dịch"""
    suspension_type = serializers.ChoiceField(choices=TradingSuspension.SUSPENSION_TYPES)
    reason = serializers.ChoiceField(choices=TradingSuspension.SUSPENSION_REASONS)
    description = serializers.CharField()
    sport_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    market_identifier = serializers.CharField(max_length=255, required=False, allow_blank=True)
    user_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    event_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    expires_at = serializers.DateTimeField(required=False, allow_null=True)

class TradingCheckSerializer(serializers.Serializer):
    """Serializer cho request kiểm tra giao dịch"""
    user_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    sport_id = serializers.CharField(max_length=255, required=False, allow_blank=True)
    market_identifier = serializers.CharField(max_length=255, required=False, allow_blank=True)
    event_id = serializers.CharField(max_length=255, required=False, allow_blank=True)

class TradingCheckResponseSerializer(serializers.Serializer):
    """Serializer cho response kiểm tra giao dịch"""
    allowed = serializers.BooleanField()
    reason = serializers.CharField()

class MarketActivityDetectionSerializer(serializers.Serializer):
    """Serializer cho request phát hiện hoạt động thị trường"""
    activity_type = serializers.ChoiceField(choices=MarketActivityMonitor.ACTIVITY_TYPES)
    market_identifier = serializers.CharField(max_length=255)
    user_id = serializers.CharField(max_length=255)
    data = serializers.JSONField(help_text='Dữ liệu cụ thể tùy theo loại hoạt động')

class UnusualVolumeDetectionSerializer(serializers.Serializer):
    """Serializer cho phát hiện volume bất thường"""
    market_identifier = serializers.CharField(max_length=255)
    current_volume = serializers.DecimalField(max_digits=15, decimal_places=2)
    historical_average = serializers.DecimalField(max_digits=15, decimal_places=2)

class RapidPriceChangeDetectionSerializer(serializers.Serializer):
    """Serializer cho phát hiện thay đổi giá nhanh"""
    market_identifier = serializers.CharField(max_length=255)
    price_changes = serializers.ListField(
        child=serializers.DictField(),
        help_text='Danh sách thay đổi giá với timestamp và price'
    )

class HighFrequencyTradingDetectionSerializer(serializers.Serializer):
    """Serializer cho phát hiện giao dịch tần số cao"""
    user_id = serializers.CharField(max_length=255)
    market_identifier = serializers.CharField(max_length=255)
    recent_orders = serializers.ListField(
        child=serializers.DictField(),
        help_text='Danh sách orders gần đây với timestamp và id'
    )

class LargeOrderDetectionSerializer(serializers.Serializer):
    """Serializer cho phát hiện lệnh lớn"""
    user_id = serializers.CharField(max_length=255)
    market_identifier = serializers.CharField(max_length=255)
    order_amount = serializers.DecimalField(max_digits=15, decimal_places=2)

class AlertAcknowledgeSerializer(serializers.Serializer):
    """Serializer cho xác nhận cảnh báo"""
    acknowledged_by = serializers.CharField(max_length=255)

class AlertResolveSerializer(serializers.Serializer):
    """Serializer cho giải quyết cảnh báo"""
    resolved_by = serializers.CharField(max_length=255)
    resolution_notes = serializers.CharField(required=False, allow_blank=True)

class DashboardSummarySerializer(serializers.Serializer):
    """Serializer cho tổng quan dashboard"""
    period_hours = serializers.IntegerField()
    timestamp = serializers.CharField()
    alerts = serializers.DictField()
    suspensions = serializers.DictField()
    market_activities = serializers.DictField()
    price_volatility = serializers.DictField()

class RecentActivitySerializer(serializers.Serializer):
    """Serializer cho hoạt động gần đây"""
    type = serializers.CharField()
    timestamp = serializers.CharField()
    severity = serializers.CharField()
    title = serializers.CharField()
    message = serializers.CharField()
    status = serializers.CharField()
    id = serializers.CharField()

class VolatilityStatsSerializer(serializers.Serializer):
    """Serializer cho thống kê biến động giá"""
    period_hours = serializers.IntegerField()
    total_detections = serializers.IntegerField()
    average_volatility = serializers.FloatField()
    max_volatility = serializers.FloatField()
    severity_breakdown = serializers.DictField()

class ConfigurationUpdateSerializer(serializers.Serializer):
    """Serializer cho cập nhật cấu hình"""
    config_value = serializers.JSONField()
    description = serializers.CharField(required=False, allow_blank=True)
    updated_by = serializers.CharField(max_length=255)

# ============================================================================
# LEGACY SERIALIZERS (Giữ lại để tương thích)
# ============================================================================

class RiskProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskProfile
        fields = '__all__'

class RiskSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskSetting
        fields = '__all__'

class PayoutLiabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = PayoutLiability
        fields = '__all__'

class OddsAdjustmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = OddsAdjustment
        fields = '__all__'

class PromotionImpactSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromotionImpact
        fields = '__all__'

class RiskLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskLog
        fields = '__all__'