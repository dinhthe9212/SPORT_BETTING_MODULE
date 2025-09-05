from rest_framework import serializers
from .models import (
    Sport, Team, Match, BetType, Odd, BetSlip, BetSelection, BetSlipPurchase,
    ResponsibleGamingPolicy, UserActivityLog, CashOutConfiguration, CashOutHistory,
    UserStatistics, Leaderboard, BettingStatistics, PerformanceMetrics,
    BetSlipOwnership, OrderBook, MarketSuspension, TradingSession, P2PTransaction
)
from django.utils import timezone

class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = '__all__'

class MatchSerializer(serializers.ModelSerializer):
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    home_team_name = serializers.CharField(source='home_team.name', read_only=True)
    away_team_name = serializers.CharField(source='away_team.name', read_only=True)
    
    # Add stake type information
    stake_type_display = serializers.CharField(source='get_stake_type_display', read_only=True)
    
    class Meta:
        model = Match
        fields = '__all__'
    
    def validate(self, data):
        """Custom validation for stake type and fixed stake value"""
        stake_type = data.get('stake_type')
        fixed_stake_value = data.get('fixed_stake_value')
        
        if stake_type == 'FIXED' and not fixed_stake_value:
            raise serializers.ValidationError(
                'Fixed stake value is required when stake type is FIXED'
            )
        
        if stake_type == 'FREE' and fixed_stake_value:
            raise serializers.ValidationError(
                'Fixed stake value should not be set when stake type is FREE'
            )
        
        return data

class BetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BetType
        fields = '__all__'

class OddSerializer(serializers.ModelSerializer):
    match_details = MatchSerializer(source='match', read_only=True)
    bet_type_name = serializers.CharField(source='bet_type.name', read_only=True)

    class Meta:
        model = Odd
        fields = '__all__'
class BetSelectionSerializer(serializers.ModelSerializer):
    odd_details = OddSerializer(source='odd', read_only=True)

    class Meta:
        model = BetSelection
        fields = '__all__'
class BetSlipSerializer(serializers.ModelSerializer):
    selections = BetSelectionSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = BetSlip
        fields = '__all__'

class BetSlipPurchaseSerializer(serializers.ModelSerializer):
    bet_slip_details = BetSlipSerializer(source='bet_slip', read_only=True)
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)

    class Meta:
        model = BetSlipPurchase
        fields = '__all__'




class ResponsibleGamingPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponsibleGamingPolicy
        fields = "__all__"
        read_only_fields = ("id", "created_at", "updated_at")

class UserActivityLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserActivityLog
        fields = "__all__"
        read_only_fields = ("id", "timestamp")


class CashOutConfigurationSerializer(serializers.ModelSerializer):
    """Serializer cho cấu hình phí Cash Out"""
    
    bookmaker_type_display = serializers.CharField(source='get_bookmaker_type_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    
    class Meta:
        model = CashOutConfiguration
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'is_valid')
    
    def validate(self, data):
        """Validation cho cấu hình phí Cash Out"""
        cash_out_fee_percentage = data.get('cash_out_fee_percentage')
        
        if cash_out_fee_percentage and cash_out_fee_percentage < 0:
            raise serializers.ValidationError('Phí Cash Out không thể âm')
        
        if cash_out_fee_percentage and cash_out_fee_percentage > 1:
            raise serializers.ValidationError('Phí Cash Out không thể vượt quá 100%')
        
        return data


class CashOutHistorySerializer(serializers.ModelSerializer):
    """Serializer cho lịch sử Cash Out"""
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    bet_slip_id = serializers.IntegerField(source='bet_slip.id', read_only=True)
    
    class Meta:
        model = CashOutHistory
        fields = '__all__'
        read_only_fields = (
            'id', 'requested_at', 'processed_at', 'completed_at', 
            'profit_loss', 'processing_time'
        )


class CashOutRequestSerializer(serializers.Serializer):
    """Serializer cho yêu cầu Cash Out"""
    
    bet_slip_id = serializers.IntegerField()
    bookmaker_type = serializers.ChoiceField(
        choices=CashOutConfiguration.BOOKMAKER_TYPE_CHOICES,
        default='SYSTEM'
    )
    bookmaker_id = serializers.CharField(default='system')


class CashOutQuoteSerializer(serializers.Serializer):
    """Serializer cho báo giá Cash Out"""
    
    bet_slip_id = serializers.IntegerField()
    fair_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    fee_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    fee_percentage = serializers.DecimalField(max_digits=5, decimal_places=4)
    cash_out_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    expiry_time = serializers.DateTimeField()
    bookmaker_config = serializers.DictField()


class CashOutConfirmationSerializer(serializers.Serializer):
    """Serializer cho xác nhận Cash Out"""
    
    bet_slip_id = serializers.IntegerField()
    confirmation_code = serializers.CharField()


class AutoOrderSetupSerializer(serializers.Serializer):
    """Serializer cho thiết lập lệnh tự động (Chốt Lời & Cắt Lỗ)"""
    
    bet_slip_id = serializers.IntegerField()
    take_profit_threshold = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        help_text='Ngưỡng chốt lời - Tự động Cash Out khi đạt mức lợi nhuận này'
    )
    stop_loss_threshold = serializers.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        required=False,
        help_text='Ngưỡng cắt lỗ - Tự động Cash Out khi giảm xuống mức thua lỗ này'
    )
    
    def validate(self, data):
        """Validation: Phải có ít nhất một ngưỡng"""
        take_profit = data.get('take_profit_threshold')
        stop_loss = data.get('stop_loss_threshold')
        
        if not take_profit and not stop_loss:
            raise serializers.ValidationError(
                'Phải có ít nhất một ngưỡng (chốt lời hoặc cắt lỗ)'
            )
        
        # Validation cho take profit threshold
        if take_profit and take_profit <= 0:
            raise serializers.ValidationError(
                'Ngưỡng chốt lời phải lớn hơn 0'
            )
        
        # Validation cho stop loss threshold
        if stop_loss and stop_loss <= 0:
            raise serializers.ValidationError(
                'Ngưỡng cắt lỗ phải lớn hơn 0'
            )
        
        return data


class AutoOrderStatusSerializer(serializers.Serializer):
    """Serializer cho trạng thái lệnh tự động"""
    
    bet_slip_id = serializers.IntegerField()
    auto_order_status = serializers.CharField()
    take_profit_threshold = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    stop_loss_threshold = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    auto_order_created_at = serializers.DateTimeField(allow_null=True)
    auto_order_triggered_at = serializers.DateTimeField(allow_null=True)
    auto_order_reason = serializers.CharField(allow_null=True)
    auto_order_enabled = serializers.BooleanField()
    
    # Thông tin bổ sung
    current_cashout_value = serializers.DecimalField(max_digits=10, decimal_places=2, allow_null=True)
    can_setup_auto_order = serializers.BooleanField()
    has_active_auto_order = serializers.BooleanField()


class AutoOrderStatisticsSerializer(serializers.Serializer):
    """Serializer cho thống kê lệnh tự động"""
    
    total_active = serializers.IntegerField()
    total_suspended = serializers.IntegerField()
    total_triggered_today = serializers.IntegerField()
    take_profit_count = serializers.IntegerField()
    stop_loss_count = serializers.IntegerField()
    last_updated = serializers.DateTimeField()
    
    cashout_history_id = serializers.IntegerField()
    user_confirmation = serializers.BooleanField()


class CashOutEligibilitySerializer(serializers.Serializer):
    """Serializer cho kiểm tra tính đủ điều kiện Cash Out"""
    
    can_cash_out = serializers.BooleanField()
    reasons = serializers.ListField(child=serializers.CharField())
    cash_out_enabled = serializers.BooleanField()
    cash_out_before_match = serializers.BooleanField()
    bet_status = serializers.CharField()
    bet_type = serializers.CharField()


class UserStatisticsSerializer(serializers.ModelSerializer):
    """Serializer cho User Statistics"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    period_display = serializers.CharField(source='get_period_display', read_only=True)
    
    class Meta:
        model = UserStatistics
        fields = [
            'id', 'user', 'user_email', 'username', 'period', 'period_display',
            'period_start', 'period_end', 'total_bets', 'total_wins', 'total_losses',
            'total_draws', 'total_stake', 'total_return', 'total_profit', 'total_fees',
            'win_rate', 'roi', 'average_odds', 'average_bet_size', 'best_win_streak',
            'current_win_streak', 'best_loss_streak', 'current_loss_streak',
            'single_bets', 'multiple_bets', 'system_bets', 'football_bets',
            'basketball_bets', 'tennis_bets', 'other_sports_bets',
            'last_updated', 'created_at'
        ]
        read_only_fields = ['id', 'win_rate', 'roi', 'average_bet_size', 'last_updated', 'created_at']


class LeaderboardSerializer(serializers.ModelSerializer):
    """Serializer cho Leaderboard"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    period_display = serializers.CharField(source='get_period_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    rank_display = serializers.CharField(source='get_rank_display', read_only=True)
    
    class Meta:
        model = Leaderboard
        fields = [
            'id', 'period', 'period_display', 'category', 'category_display',
            'period_start', 'period_end', 'user', 'user_email', 'username',
            'rank', 'rank_display', 'points', 'total_profit', 'win_rate',
            'total_bets', 'total_stake', 'win_streak', 'roi', 'is_featured',
            'featured_reason', 'last_updated', 'created_at'
        ]
        read_only_fields = ['id', 'rank_display', 'last_updated', 'created_at']


class BettingStatisticsSerializer(serializers.ModelSerializer):
    """Serializer cho Betting Statistics"""
    period_display = serializers.CharField(source='get_period_display', read_only=True)
    
    class Meta:
        model = BettingStatistics
        fields = [
            'id', 'period', 'period_display', 'period_start', 'period_end',
            'total_bets_placed', 'total_unique_users', 'total_matches',
            'total_stake_amount', 'total_return_amount', 'total_profit', 'house_edge',
            'single_bets_count', 'multiple_bets_count', 'system_bets_count',
            'football_bets', 'basketball_bets', 'tennis_bets', 'other_sports_bets',
            'free_stake_bets', 'fixed_stake_bets', 'total_cashout_requests',
            'total_cashout_amount', 'cashout_success_rate', 'average_bet_size',
            'average_odds', 'win_rate', 'last_updated', 'created_at'
        ]
        read_only_fields = ['id', 'house_edge', 'win_rate', 'average_bet_size', 'last_updated', 'created_at']


class PerformanceMetricsSerializer(serializers.ModelSerializer):
    """Serializer cho Performance Metrics"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    sport_name = serializers.CharField(source='sport.name', read_only=True)
    bet_type_name = serializers.CharField(source='bet_type.name', read_only=True)
    
    class Meta:
        model = PerformanceMetrics
        fields = [
            'id', 'user', 'user_email', 'username', 'sport', 'sport_name',
            'bet_type', 'bet_type_name', 'total_bets', 'total_wins', 'total_losses',
            'success_rate', 'win_rate', 'total_stake', 'total_return', 'profit_loss',
            'roi', 'average_odds', 'best_odds', 'worst_odds', 'first_bet_date',
            'last_bet_date', 'last_updated', 'created_at'
        ]
        read_only_fields = ['id', 'success_rate', 'win_rate', 'roi', 'last_updated', 'created_at']


class LeaderboardSummarySerializer(serializers.Serializer):
    """Serializer cho tổng quan Leaderboard"""
    period = serializers.CharField()
    category = serializers.CharField()
    total_participants = serializers.IntegerField()
    top_3 = LeaderboardSerializer(many=True)
    user_rank = serializers.IntegerField(required=False, allow_null=True)
    user_points = serializers.IntegerField(required=False, allow_null=True)
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()


class StatisticsSummarySerializer(serializers.Serializer):
    """Serializer cho tổng quan thống kê"""
    period = serializers.CharField()
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()
    
    # User statistics
    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    new_users = serializers.IntegerField()
    
    # Betting statistics
    total_bets = serializers.IntegerField()
    total_stake = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_return = serializers.DecimalField(max_digits=15, decimal_places=2)
    house_profit = serializers.DecimalField(max_digits=15, decimal_places=2)
    house_edge = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Performance metrics
    average_bet_size = serializers.DecimalField(max_digits=10, decimal_places=2)
    win_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    cashout_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    
    # Top performers
    top_profit_users = serializers.ListField(child=serializers.DictField())
    top_win_rate_users = serializers.ListField(child=serializers.DictField())
    top_volume_users = serializers.ListField(child=serializers.DictField())


class UserPerformanceSummarySerializer(serializers.Serializer):
    """Serializer cho tổng quan hiệu suất người dùng"""
    user_id = serializers.IntegerField()
    user_email = serializers.CharField()
    username = serializers.CharField()
    
    # Overall performance
    total_bets = serializers.IntegerField()
    total_wins = serializers.IntegerField()
    win_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    total_profit = serializers.DecimalField(max_digits=15, decimal_places=2)
    roi = serializers.DecimalField(max_digits=8, decimal_places=4)
    
    # Streaks
    current_win_streak = serializers.IntegerField()
    best_win_streak = serializers.IntegerField()
    
    # Sports performance
    sports_performance = serializers.ListField(child=serializers.DictField())
    
    # Recent activity
    last_bet_date = serializers.DateTimeField()
    total_stake = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_bet_size = serializers.DecimalField(max_digits=10, decimal_places=2)


class BetSlipOwnershipSerializer(serializers.ModelSerializer):
    """Serializer cho quản lý quyền sở hữu phân mảnh"""
    
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    bet_slip_details = BetSlipSerializer(source='bet_slip', read_only=True)
    ownership_value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    potential_payout = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = BetSlipOwnership
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'ownership_value', 'potential_payout')


class OrderBookSerializer(serializers.ModelSerializer):
    """Serializer cho sổ lệnh mua/bán P2P"""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    bet_slip_details = BetSlipSerializer(source='bet_slip', read_only=True)
    remaining_quantity = serializers.IntegerField(read_only=True)
    total_value = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = OrderBook
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'filled_quantity', 'remaining_quantity', 'total_value', 'is_expired')
    
    def validate(self, data):
        """Validation cho lệnh đặt"""
        # Kiểm tra giá không được âm
        if data.get('price', 0) <= 0:
            raise serializers.ValidationError("Giá phải lớn hơn 0")
        
        # Kiểm tra số lượng không được âm
        if data.get('quantity', 0) <= 0:
            raise serializers.ValidationError("Số lượng phải lớn hơn 0")
        
        # Kiểm tra thời gian hết hạn phải trong tương lai
        if data.get('expires_at'):
            if data['expires_at'] <= timezone.now():
                raise serializers.ValidationError("Thời gian hết hạn phải trong tương lai")
        
        return data


class MarketSuspensionSerializer(serializers.ModelSerializer):
    """Serializer cho quản lý tạm khóa thị trường"""
    
    match_details = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    suspension_duration = serializers.SerializerMethodField()
    
    class Meta:
        model = MarketSuspension
        fields = '__all__'
        read_only_fields = ('id', 'suspended_at', 'created_at', 'updated_at', 'is_active', 'suspension_duration')
    
    def get_match_details(self, obj):
        """Lấy thông tin chi tiết trận đấu"""
        return {
            'id': obj.match.id,
            'home_team': obj.match.home_team.name,
            'away_team': obj.match.away_team.name,
            'start_time': obj.match.start_time,
            'status': obj.match.status
        }
    
    def get_suspension_duration(self, obj):
        """Lấy thời gian đã tạm khóa"""
        if obj.resumed_at:
            return (obj.resumed_at - obj.suspended_at).total_seconds() / 60
        return (timezone.now() - obj.suspended_at).total_seconds() / 60


class TradingSessionSerializer(serializers.ModelSerializer):
    """Serializer cho phiên giao dịch P2P"""
    
    match_details = serializers.SerializerMethodField()
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    is_collecting = serializers.BooleanField(read_only=True)
    is_matching = serializers.BooleanField(read_only=True)
    time_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = TradingSession
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at', 'total_orders', 'matched_orders', 'is_active', 'is_collecting', 'is_matching', 'time_remaining')
    
    def get_match_details(self, obj):
        """Lấy thông tin chi tiết trận đấu"""
        return {
            'id': obj.match.id,
            'home_team': obj.match.home_team.name,
            'away_team': obj.match.away_team.name,
            'start_time': obj.match.start_time,
            'status': obj.match.status
        }
    
    def get_time_remaining(self, obj):
        """Lấy thời gian còn lại của phiên"""
        if obj.time_remaining:
            return obj.time_remaining.total_seconds()
        return 0


class P2PTransactionSerializer(serializers.ModelSerializer):
    """Serializer cho giao dịch P2P"""
    
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    bet_slip_details = BetSlipSerializer(source='bet_slip', read_only=True)
    buy_order_details = OrderBookSerializer(source='buy_order', read_only=True)
    sell_order_details = OrderBookSerializer(source='sell_order', read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    is_failed = serializers.BooleanField(read_only=True)
    processing_time = serializers.SerializerMethodField()
    
    class Meta:
        model = P2PTransaction
        fields = '__all__'
        read_only_fields = ('id', 'transaction_id', 'created_at', 'updated_at', 'is_completed', 'is_failed', 'processing_time')
    
    def get_processing_time(self, obj):
        """Lấy thời gian xử lý giao dịch"""
        if obj.processing_time:
            return obj.processing_time.total_seconds()
        return None
    
    def validate(self, data):
        """Validation cho giao dịch P2P"""
        # Kiểm tra người mua và người bán không được giống nhau
        if data.get('buyer') == data.get('seller'):
            raise serializers.ValidationError("Người mua và người bán không được giống nhau")
        
        # Kiểm tra số lượng không được âm
        if data.get('quantity', 0) <= 0:
            raise serializers.ValidationError("Số lượng phải lớn hơn 0")
        
        # Kiểm tra tỷ lệ sở hữu hợp lệ
        ownership_percentage = data.get('ownership_percentage', 0)
        if ownership_percentage <= 0 or ownership_percentage > 100:
            raise serializers.ValidationError("Tỷ lệ sở hữu phải từ 0.01% đến 100%")
        
        return data


