from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Sport, Team, Match, BetType, Odd, OddsHistory, BetSlip, BetSelection,
    BetSlipPurchase, ResponsibleGamingPolicy, UserActivityLog,
    CashOutConfiguration, CashOutHistory, UserStatistics, Leaderboard, BettingStatistics, PerformanceMetrics
)
from django.utils import timezone
from .models import (
    BetSlipOwnership, OrderBook, MarketSuspension, TradingSession, P2PTransaction
)

@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'sport', 'country']
    list_filter = ['sport', 'country']
    search_fields = ['name', 'country']

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['home_team', 'away_team', 'sport', 'start_time', 'status', 'stake_type']
    list_filter = ['status', 'sport', 'stake_type', 'start_time']
    search_fields = ['home_team__name', 'away_team__name', 'sport__name']
    date_hierarchy = 'start_time'

@admin.register(BetType)
class BetTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'description']

@admin.register(Odd)
class OddAdmin(admin.ModelAdmin):
    list_display = [
        'match_display', 'bet_type', 'outcome', 'value', 'odds_type', 
        'odds_status', 'risk_multiplier', 'current_liability', 'is_active'
    ]
    list_filter = [
        'odds_type', 'odds_status', 'is_active', 'auto_adjust_enabled',
        'match__sport', 'bet_type'
    ]
    search_fields = [
        'match__home_team__name', 'match__away_team__name', 
        'outcome', 'bet_type__name'
    ]
    readonly_fields = [
        'last_updated', 'last_risk_update', 'current_liability'
    ]
    fieldsets = (
        ('Basic Information', {
            'fields': ('match', 'bet_type', 'outcome', 'value', 'is_active')
        }),
        ('Odds Configuration', {
            'fields': (
                'odds_type', 'odds_status', 'base_value', 'min_value', 
                'max_value', 'adjustment_step'
            )
        }),
        ('Risk Management', {
            'fields': (
                'risk_multiplier', 'liability_threshold', 'current_liability',
                'auto_adjust_enabled', 'risk_profile_id'
            )
        }),
        ('Metadata', {
            'fields': ('created_by', 'last_updated', 'last_risk_update')
        }),
    )
    
    def match_display(self, obj):
        """Hiển thị thông tin match một cách gọn gàng"""
        if obj.match:
            return f"{obj.match.home_team.name} vs {obj.match.away_team.name}"
        return "N/A"
    match_display.short_description = 'Match'
    
    def get_queryset(self, request):
        """Tối ưu query với select_related"""
        return super().get_queryset(request).select_related(
            'match__home_team', 'match__away_team', 'match__sport', 'bet_type'
        )

@admin.register(OddsHistory)
class OddsHistoryAdmin(admin.ModelAdmin):
    list_display = [
        'odd_display', 'change_reason', 'old_value', 'new_value', 
        'change_percentage_display', 'timestamp', 'changed_by'
    ]
    list_filter = [
        'change_reason', 'timestamp'
    ]
    search_fields = [
        'odd__match__home_team__name', 'odd__match__away_team__name',
        'odd__outcome', 'change_reason'
    ]
    readonly_fields = [
        'timestamp', 'change_percentage', 'is_significant_change'
    ]
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Change Information', {
            'fields': ('odd', 'change_reason', 'old_value', 'new_value')
        }),
        ('Risk Data', {
            'fields': ('risk_liability', 'risk_multiplier', 'risk_profile_id')
        }),
        ('Additional Data', {
            'fields': ('additional_data', 'ip_address')
        }),
        ('Metadata', {
            'fields': ('changed_by', 'timestamp', 'change_percentage', 'is_significant_change')
        }),
    )
    
    def odd_display(self, obj):
        """Hiển thị thông tin odds một cách gọn gàng"""
        if obj.odd:
            match = obj.odd.match
            return f"{match.home_team.name} vs {match.away_team.name} - {obj.odd.outcome}"
        return "N/A"
    odd_display.short_description = 'Odds'
    
    def change_percentage_display(self, obj):
        """Hiển thị phần trăm thay đổi với màu sắc"""
        if obj.change_percentage > 0:
            color = 'green'
            symbol = '↗'
        elif obj.change_percentage < 0:
            color = 'red'
            symbol = '↘'
        else:
            color = 'gray'
            symbol = '→'
        
        return format_html(
            '<span style="color: {};">{} {:.2f}%</span>',
            color, symbol, abs(obj.change_percentage)
        )
    change_percentage_display.short_description = 'Change %'
    
    def get_queryset(self, request):
        """Tối ưu query với select_related"""
        return super().get_queryset(request).select_related(
            'odd__match__home_team', 'odd__match__away_team', 'odd__bet_type', 'changed_by'
        )

@admin.register(BetSlip)
class BetSlipAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'bet_type', 'bet_status', 'total_stake', 
        'potential_payout', 'cash_out_status', 'auto_order_status', 'created_at'
    ]
    
    list_filter = [
        'bet_type', 'bet_status', 'cash_out_enabled', 'cash_out_before_match', 
        'auto_order_enabled', 'auto_order_status', 'created_at'
    ]
    
    search_fields = ['user__username', 'id']
    
    readonly_fields = [
        'created_at', 'confirmed_at', 'cancelled_at', 'settled_at',
        'cash_out_at', 'cash_out_requested_at', 'can_cash_out',
        'auto_order_created_at', 'auto_order_triggered_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'bet_type', 'bet_status', 'total_stake', 'potential_payout')
        }),
        ('Cash Out Configuration', {
            'fields': (
                'cash_out_enabled', 'cash_out_before_match', 'is_cash_out_available'
            )
        }),
        ('Cash Out Details', {
            'fields': (
                'cash_out_value', 'cash_out_fair_value', 'cash_out_fee_amount', 
                'cash_out_fee_percentage', 'cash_out_at', 'cash_out_requested_at'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'confirmed_at', 'cancelled_at', 'settled_at')
        }),
        ('Saga Integration', {
            'fields': ('saga_transaction_id', 'wallet_transaction_id')
        }),
        ('Status', {
            'fields': ('is_settled', 'is_won', 'can_cash_out')
        }),
        ('Auto Order Management', {
            'fields': (
                'auto_order_enabled', 'auto_order_status', 'take_profit_threshold',
                'stop_loss_threshold', 'auto_order_created_at', 'auto_order_triggered_at',
                'auto_order_reason', 'can_setup_auto_order', 'has_active_auto_order'
            )
        }),
    )
    
    actions = ['enable_cash_out', 'disable_cash_out', 'reset_cash_out', 
               'enable_auto_orders', 'disable_auto_orders', 'suspend_auto_orders']
    
    def cash_out_status(self, obj):
        """Hiển thị trạng thái Cash Out với màu sắc"""
        if obj.bet_status == 'CASHED_OUT':
            return format_html(
                '<span style="color: green;">✓ Cashed Out</span>'
            )
        elif obj.bet_status == 'CASHING_OUT':
            return format_html(
                '<span style="color: orange;">⏳ Processing</span>'
            )
        elif obj.can_cash_out:
            return format_html(
                '<span style="color: blue;">💳 Available</span>'
            )
        else:
            return format_html(
                '<span style="color: red;">✗ Not Available</span>'
            )
    cash_out_status.short_description = 'Cash Out Status'
    
    @admin.action(description='Enable Cash Out for selected bet slips')
    def enable_cash_out(self, request, queryset):
        updated = queryset.update(cash_out_enabled=True)
        self.message_user(request, f'{updated} bet slips đã được bật Cash Out.')
    
    @admin.action(description='Disable Cash Out for selected bet slips')
    def disable_cash_out(self, request, queryset):
        updated = queryset.update(cash_out_enabled=False)
        self.message_user(request, f'{updated} bet slips đã được tắt Cash Out.')
    
    @admin.action(description='Reset Cash Out data for selected bet slips')
    def reset_cash_out(self, request, queryset):
        updated = queryset.update(
            cash_out_value=None,
            cash_out_fair_value=None,
            cash_out_fee_amount=None,
            cash_out_fee_percentage=None,
            cash_out_at=None,
            cash_out_requested_at=None,
            is_cash_out_available=False
        )
        self.message_user(request, f'{updated} bet slips đã được reset Cash Out data.')
    
    @admin.action(description='Enable Auto Orders for selected bet slips')
    def enable_auto_orders(self, request, queryset):
        updated = queryset.update(auto_order_enabled=True)
        self.message_user(request, f'{updated} bet slips đã được bật lệnh tự động.')
    
    @admin.action(description='Disable Auto Orders for selected bet slips')
    def disable_auto_orders(self, request, queryset):
        updated = queryset.update(auto_order_enabled=False)
        self.message_user(request, f'{updated} bet slips đã được tắt lệnh tự động.')
    
    @admin.action(description='Suspend Auto Orders for selected bet slips')
    def suspend_auto_orders(self, request, queryset):
        updated = queryset.update(auto_order_status='SUSPENDED')
        self.message_user(request, f'{updated} bet slips đã được tạm dừng lệnh tự động.')

@admin.register(BetSelection)
class BetSelectionAdmin(admin.ModelAdmin):
    list_display = ['bet_slip', 'odd_display', 'selected_value', 'odds_at_placement', 'placement_timestamp']
    list_filter = ['placement_timestamp']
    search_fields = ['bet_slip__id', 'odd__outcome']

    def odd_display(self, obj):
        if obj.odd:
            match = obj.odd.match
            return f"{match.home_team.name} vs {match.away_team.name} - {obj.odd.outcome}"
        return "N/A"
    odd_display.short_description = 'Odds'

@admin.register(BetSlipPurchase)
class BetSlipPurchaseAdmin(admin.ModelAdmin):
    list_display = ['seller', 'buyer', 'bet_slip', 'price', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_p2p_offer', 'is_fractional', 'created_at']
    search_fields = ['seller__username', 'buyer__username', 'bet_slip__id']

@admin.register(ResponsibleGamingPolicy)
class ResponsibleGamingPolicyAdmin(admin.ModelAdmin):
    list_display = ['user', 'deposit_limit_daily', 'loss_limit_daily', 'session_limit_minutes']
    list_filter = ['created_at']
    search_fields = ['user__username']

@admin.register(UserActivityLog)
class UserActivityLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'timestamp', 'ip_address']
    list_filter = ['activity_type', 'timestamp']
    search_fields = ['user__username', 'activity_type']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'

# Custom admin actions
@admin.action(description='Enable auto-adjust for selected odds')
def enable_auto_adjust(modeladmin, request, queryset):
    updated = queryset.update(auto_adjust_enabled=True)
    modeladmin.message_user(request, f'{updated} odds đã được bật tự động điều chỉnh.')

@admin.action(description='Disable auto-adjust for selected odds')
def disable_auto_adjust(modeladmin, request, queryset):
    updated = queryset.update(auto_adjust_enabled=False)
    modeladmin.message_user(request, f'{updated} odds đã được tắt tự động điều chỉnh.')

@admin.action(description='Set odds type to RISK_BASED')
def set_risk_based(modeladmin, request, queryset):
    updated = queryset.update(odds_type='RISK_BASED')
    modeladmin.message_user(request, f'{updated} odds đã được chuyển sang RISK_BASED.')

# Add custom actions to OddAdmin
OddAdmin.actions = [enable_auto_adjust, disable_auto_adjust, set_risk_based]


@admin.register(CashOutConfiguration)
class CashOutConfigurationAdmin(admin.ModelAdmin):
    """Admin cho cấu hình phí Cash Out"""
    
    list_display = [
        'bookmaker_type', 'bookmaker_id', 'fee_display', 
        'cash_out_enabled', 'cash_out_before_match', 'is_valid', 'created_at'
    ]
    
    list_filter = [
        'bookmaker_type', 'cash_out_enabled', 'cash_out_before_match', 
        'is_active', 'created_at'
    ]
    
    search_fields = ['bookmaker_id']
    
    readonly_fields = ['created_at', 'updated_at', 'is_valid', 'fee_display']
    
    fieldsets = (
        ('Bookmaker Information', {
            'fields': ('bookmaker_type', 'bookmaker_id')
        }),
        ('Cash Out Fee Configuration', {
            'description': 'Để trống phí cụ thể để sử dụng margin của sự kiện (cho nhà cái hệ thống)',
            'fields': (
                'cash_out_fee_percentage', 'min_cash_out_amount', 'max_cash_out_amount'
            )
        }),
        ('Feature Configuration', {
            'fields': ('cash_out_enabled', 'cash_out_before_match')
        }),
        ('Validity Period', {
            'fields': ('valid_from', 'valid_until')
        }),
        ('Metadata', {
            'fields': ('created_by', 'is_active', 'created_at', 'updated_at')
        }),
    )
    
    def fee_display(self, obj):
        """Hiển thị phí với logic đúng"""
        if obj.cash_out_fee_percentage is not None:
            return f"{float(obj.cash_out_fee_percentage) * 100:.1f}% (Cấu hình cụ thể)"
        elif obj.bookmaker_type == 'SYSTEM':
            return "Sử dụng Margin sự kiện"
        else:
            return "0% (Mặc định)"
    fee_display.short_description = 'Phí Cash Out'
    
    def is_valid(self, obj):
        """Hiển thị trạng thái hiệu lực với màu sắc"""
        if obj.is_valid:
            return format_html(
                '<span style="color: green;">✓ Valid</span>'
            )
        else:
            return format_html(
                '<span style="color: red;">✗ Invalid</span>'
            )
    is_valid.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        """Tự động set created_by khi tạo mới"""
        if not change:  # Nếu là tạo mới
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_queryset(self, request):
        """Tối ưu query"""
        return super().get_queryset(request).select_related('created_by')


@admin.register(CashOutHistory)
class CashOutHistoryAdmin(admin.ModelAdmin):
    """Admin cho lịch sử Cash Out"""
    
    list_display = [
        'id', 'user', 'bet_slip_display', 'status', 'requested_amount', 
        'final_amount', 'fee_amount', 'profit_loss_display', 'requested_at'
    ]
    
    list_filter = [
        'status', 'requested_at', 'processed_at', 'completed_at'
    ]
    
    search_fields = [
        'user__username', 'bet_slip__id', 'saga_transaction_id'
    ]
    
    readonly_fields = [
        'requested_at', 'processed_at', 'completed_at', 'profit_loss'
    ]
    
    date_hierarchy = 'requested_at'
    
    fieldsets = (
        ('Transaction Information', {
            'fields': (
                'user', 'bet_slip', 'status', 'saga_transaction_id', 'wallet_transaction_id'
            )
        }),
        ('Cash Out Details', {
            'fields': (
                'requested_amount', 'fair_value', 'fee_percentage', 'fee_amount', 'final_amount'
            )
        }),
        ('Odds Information', {
            'fields': ('original_odds', 'live_odds')
        }),
        ('Timestamps', {
            'fields': ('requested_at', 'processed_at', 'completed_at')
        }),
        ('Additional Information', {
            'fields': ('profit_loss', 'failure_reason', 'ip_address', 'user_agent')
        }),
    )
    
    def bet_slip_display(self, obj):
        """Hiển thị thông tin bet slip"""
        if obj.bet_slip:
            return f"#{obj.bet_slip.id} - {obj.bet_slip.user.username}"
        return "N/A"
    bet_slip_display.short_description = 'Bet Slip'
    
    def profit_loss_display(self, obj):
        """Hiển thị lãi/lỗ với màu sắc"""
        if obj.profit_loss is None:
            return "N/A"
        
        if obj.profit_loss > 0:
            color = 'green'
            symbol = '+'
        elif obj.profit_loss < 0:
            color = 'red'
            symbol = ''
        else:
            color = 'gray'
            symbol = ''
        
        return format_html(
            '<span style="color: {};">{}{:.2f}</span>',
            color, symbol, obj.profit_loss
        )
    profit_loss_display.short_description = 'Profit/Loss'
    
    def get_queryset(self, request):
        """Tối ưu query với select_related"""
        return super().get_queryset(request).select_related(
            'user', 'bet_slip', 'bet_slip__user'
        )

@admin.register(UserStatistics)
class UserStatisticsAdmin(admin.ModelAdmin):
    """Admin cho User Statistics"""
    list_display = [
        'user', 'period', 'period_start', 'total_bets', 'total_wins', 
        'win_rate', 'total_profit', 'roi', 'current_win_streak'
    ]
    list_filter = ['period', 'period_start', 'user']
    search_fields = ['user__email', 'user__username']
    readonly_fields = [
        'win_rate', 'roi', 'average_bet_size', 'last_updated', 'created_at'
    ]
    ordering = ['-period_start', '-total_profit']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('user', 'period', 'period_start', 'period_end')
        }),
        ('Thống kê cơ bản', {
            'fields': ('total_bets', 'total_wins', 'total_losses', 'total_draws')
        }),
        ('Thống kê tài chính', {
            'fields': ('total_stake', 'total_return', 'total_profit', 'total_fees')
        }),
        ('Tỷ lệ và hiệu suất', {
            'fields': ('win_rate', 'roi', 'average_odds', 'average_bet_size')
        }),
        ('Chuỗi thắng/thua', {
            'fields': ('best_win_streak', 'current_win_streak', 'best_loss_streak', 'current_loss_streak')
        }),
        ('Thống kê theo loại cược', {
            'fields': ('single_bets', 'multiple_bets', 'system_bets')
        }),
        ('Thống kê theo môn thể thao', {
            'fields': ('football_bets', 'basketball_bets', 'tennis_bets', 'other_sports_bets')
        }),
        ('Metadata', {
            'fields': ('last_updated', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Leaderboard)
class LeaderboardAdmin(admin.ModelAdmin):
    """Admin cho Leaderboard"""
    list_display = [
        'rank', 'user', 'period', 'category', 'points', 'total_profit', 
        'win_rate', 'is_featured'
    ]
    list_filter = ['period', 'category', 'is_featured', 'period_start']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['last_updated', 'created_at']
    ordering = ['period', 'category', 'rank']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('period', 'category', 'period_start', 'period_end')
        }),
        ('Người dùng và xếp hạng', {
            'fields': ('user', 'rank', 'rank_display', 'points')
        }),
        ('Chỉ số xếp hạng', {
            'fields': ('total_profit', 'win_rate', 'total_bets', 'total_stake', 'win_streak', 'roi')
        }),
        ('Highlight', {
            'fields': ('is_featured', 'featured_reason')
        }),
        ('Metadata', {
            'fields': ('last_updated', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['refresh_leaderboard']
    
    def refresh_leaderboard(self, request, queryset):
        """Làm mới bảng xếp hạng"""
        from .services import LeaderboardService
        
        updated_count = 0
        for entry in queryset:
            try:
                LeaderboardService.update_leaderboard(entry.period, entry.category)
                updated_count += 1
            except Exception as e:
                self.message_user(request, f"Lỗi khi cập nhật {entry}: {str(e)}", level='ERROR')
        
        self.message_user(request, f"Đã cập nhật {updated_count} bảng xếp hạng")
    
    refresh_leaderboard.short_description = "Làm mới bảng xếp hạng"


@admin.register(BettingStatistics)
class BettingStatisticsAdmin(admin.ModelAdmin):
    """Admin cho Betting Statistics"""
    list_display = [
        'period', 'period_start', 'total_bets_placed', 'total_unique_users',
        'total_stake_amount', 'house_edge', 'win_rate'
    ]
    list_filter = ['period', 'period_start']
    readonly_fields = [
        'house_edge', 'win_rate', 'average_bet_size', 'last_updated', 'created_at'
    ]
    ordering = ['-period_start', '-period']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('period', 'period_start', 'period_end')
        }),
        ('Thống kê tổng quan', {
            'fields': ('total_bets_placed', 'total_unique_users', 'total_matches')
        }),
        ('Thống kê tài chính', {
            'fields': ('total_stake_amount', 'total_return_amount', 'total_profit', 'house_edge')
        }),
        ('Thống kê theo loại cược', {
            'fields': ('single_bets_count', 'multiple_bets_count', 'system_bets_count')
        }),
        ('Thống kê theo môn thể thao', {
            'fields': ('football_bets', 'basketball_bets', 'tennis_bets', 'other_sports_bets')
        }),
        ('Thống kê theo loại stake', {
            'fields': ('free_stake_bets', 'fixed_stake_bets')
        }),
        ('Thống kê Cash Out', {
            'fields': ('total_cashout_requests', 'total_cashout_amount', 'cashout_success_rate')
        }),
        ('Thống kê hiệu suất', {
            'fields': ('average_bet_size', 'average_odds', 'win_rate')
        }),
        ('Metadata', {
            'fields': ('last_updated', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['refresh_statistics']
    
    def refresh_statistics(self, request, queryset):
        """Làm mới thống kê"""
        from .services import BettingStatisticsService
        
        updated_count = 0
        for stats in queryset:
            try:
                BettingStatisticsService.calculate_betting_statistics(stats.period)
                updated_count += 1
            except Exception as e:
                self.message_user(request, f"Lỗi khi cập nhật {stats}: {str(e)}", level='ERROR')
        
        self.message_user(request, f"Đã cập nhật {updated_count} thống kê")
    
    refresh_statistics.short_description = "Làm mới thống kê"


@admin.register(PerformanceMetrics)
class PerformanceMetricsAdmin(admin.ModelAdmin):
    """Admin cho Performance Metrics"""
    list_display = [
        'user', 'sport', 'bet_type', 'total_bets', 'win_rate', 
        'roi', 'total_stake'
    ]
    list_filter = ['sport', 'bet_type']
    search_fields = ['user__email', 'user__username']
    readonly_fields = [
        'success_rate', 'win_rate', 'roi', 'last_updated', 'created_at'
    ]
    ordering = ['-success_rate', '-roi']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('user', 'sport', 'bet_type')
        }),
        ('Thống kê cơ bản', {
            'fields': ('total_bets', 'total_wins', 'total_losses')
        }),
        ('Tỷ lệ và hiệu suất', {
            'fields': ('success_rate', 'win_rate')
        }),
        ('Thống kê tài chính', {
            'fields': ('total_stake', 'total_return', 'profit_loss', 'roi')
        }),
        ('Thống kê odds', {
            'fields': ('average_odds', 'best_odds', 'worst_odds')
        }),
        ('Thống kê theo thời gian', {
            'fields': ('first_bet_date', 'last_bet_date')
        }),
        ('Metadata', {
            'fields': ('last_updated', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['refresh_metrics']
    
    def refresh_metrics(self, request, queryset):
        """Làm mới metrics"""
        from .services import PerformanceMetricsService
        
        updated_count = 0
        for metrics in queryset:
            try:
                PerformanceMetricsService.calculate_performance_metrics(
                    user=metrics.user,
                    sport=metrics.sport,
                    bet_type=metrics.bet_type
                )
                updated_count += 1
            except Exception as e:
                self.message_user(request, f"Lỗi khi cập nhật {metrics}: {str(e)}", level='ERROR')
        
        self.message_user(request, f"Đã cập nhật {updated_count} metrics")
    
    refresh_metrics.short_description = "Làm mới metrics"


@admin.register(BetSlipOwnership)
class BetSlipOwnershipAdmin(admin.ModelAdmin):
    """Admin cho quản lý quyền sở hữu phân mảnh phiếu cược"""
    
    list_display = [
        'id', 'owner', 'bet_slip', 'ownership_percentage', 
        'ownership_value', 'potential_payout', 'is_active', 'acquired_at'
    ]
    
    list_filter = [
        'is_active', 'acquired_at', 'ownership_percentage'
    ]
    
    search_fields = [
        'owner__username', 'bet_slip__id'
    ]
    
    readonly_fields = [
        'ownership_value', 'potential_payout', 'acquired_at'
    ]
    
    fieldsets = (
        ('Thông tin sở hữu', {
            'fields': ('owner', 'bet_slip', 'ownership_percentage', 'acquired_price')
        }),
        ('Tính toán tự động', {
            'fields': ('ownership_value', 'potential_payout')
        }),
        ('Trạng thái', {
            'fields': ('is_active', 'acquired_at')
        }),
    )
    
    def ownership_value(self, obj):
        """Hiển thị giá trị sở hữu"""
        return f"{obj.ownership_value:,.0f} VNĐ"
    ownership_value.short_description = 'Giá trị sở hữu'
    
    def potential_payout(self, obj):
        """Hiển thị tiền thắng tiềm năng"""
        return f"{obj.potential_payout:,.0f} VNĐ"
    potential_payout.short_description = 'Tiền thắng tiềm năng'


@admin.register(OrderBook)
class OrderBookAdmin(admin.ModelAdmin):
    """Admin cho sổ lệnh mua/bán P2P"""
    
    list_display = [
        'id', 'order_type', 'user', 'bet_slip', 'price', 'quantity', 
        'filled_quantity', 'status', 'is_fractional', 'created_at'
    ]
    
    list_filter = [
        'order_type', 'status', 'is_fractional', 'allow_partial_fill', 'created_at'
    ]
    
    search_fields = [
        'user__username', 'bet_slip__id', 'price'
    ]
    
    readonly_fields = [
        'remaining_quantity', 'total_value', 'is_expired', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Thông tin lệnh', {
            'fields': ('order_type', 'bet_slip', 'user', 'price', 'quantity')
        }),
        ('Tùy chọn', {
            'fields': ('allow_partial_fill', 'is_fractional', 'expires_at')
        }),
        ('Trạng thái', {
            'fields': ('status', 'filled_quantity')
        }),
        ('Tính toán tự động', {
            'fields': ('remaining_quantity', 'total_value', 'is_expired')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def remaining_quantity(self, obj):
        """Hiển thị số lượng còn lại"""
        return obj.remaining_quantity
    remaining_quantity.short_description = 'Số lượng còn lại'
    
    def total_value(self, obj):
        """Hiển thị tổng giá trị"""
        return f"{obj.total_value:,.0f} VNĐ"
    total_value.short_description = 'Tổng giá trị'
    
    def is_expired(self, obj):
        """Hiển thị trạng thái hết hạn"""
        return obj.is_expired
    is_expired.short_description = 'Hết hạn'
    is_expired.boolean = True


@admin.register(MarketSuspension)
class MarketSuspensionAdmin(admin.ModelAdmin):
    """Admin cho quản lý tạm khóa thị trường P2P"""
    
    list_display = [
        'id', 'match', 'suspension_type', 'status', 'p2p_orders_suspended',
        'suspended_at', 'resumed_at', 'duration_display'
    ]
    
    list_filter = [
        'suspension_type', 'status', 'p2p_orders_suspended', 
        'new_bets_suspended', 'cash_out_suspended', 'suspended_at'
    ]
    
    search_fields = [
        'match__home_team__name', 'match__away_team__name', 'reason'
    ]
    
    readonly_fields = [
        'is_active', 'suspension_duration', 'suspended_at', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Thông tin tạm khóa', {
            'fields': ('match', 'suspension_type', 'status', 'duration_minutes')
        }),
        ('Phạm vi tạm khóa', {
            'fields': ('p2p_orders_suspended', 'new_bets_suspended', 'cash_out_suspended')
        }),
        ('Thời gian', {
            'fields': ('suspended_at', 'resumed_at')
        }),
        ('Thông tin bổ sung', {
            'fields': ('reason', 'api_event_data')
        }),
        ('Metadata', {
            'fields': ('created_by', 'is_active', 'created_at', 'updated_at')
        }),
    )
    
    def duration_display(self, obj):
        """Hiển thị thời gian tạm khóa"""
        if obj.resumed_at:
            duration = obj.resumed_at - obj.suspended_at
            return f"{duration.total_seconds() / 60:.1f} phút"
        elif obj.is_active:
            duration = timezone.now() - obj.suspended_at
            return f"{duration.total_seconds() / 60:.1f} phút"
        return "N/A"
    duration_display.short_description = 'Thời gian tạm khóa'
    
    def is_active(self, obj):
        """Hiển thị trạng thái hoạt động"""
        return obj.is_active
    is_active.short_description = 'Đang tạm khóa'
    is_active.boolean = True


@admin.register(TradingSession)
class TradingSessionAdmin(admin.ModelAdmin):
    """Admin cho quản lý phiên giao dịch P2P"""
    
    list_display = [
        'id', 'match', 'session_type', 'status', 'total_orders', 
        'matched_orders', 'start_time', 'end_time', 'is_active'
    ]
    
    list_filter = [
        'session_type', 'status', 'created_at'
    ]
    
    search_fields = [
        'match__home_team__name', 'match__away_team__name'
    ]
    
    readonly_fields = [
        'is_active', 'is_collecting', 'is_matching', 'time_remaining', 
        'total_orders', 'matched_orders', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Thông tin phiên', {
            'fields': ('match', 'session_type', 'status')
        }),
        ('Thời gian phiên', {
            'fields': ('start_time', 'end_time', 'collection_duration', 'matching_duration')
        }),
        ('Quản lý lệnh', {
            'fields': ('orders_collected', 'total_orders', 'matched_orders')
        }),
        ('Trạng thái', {
            'fields': ('is_active', 'is_collecting', 'is_matching', 'time_remaining')
        }),
        ('Kết quả', {
            'fields': ('session_results',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    
    def is_active(self, obj):
        """Hiển thị trạng thái hoạt động"""
        return obj.is_active
    is_active.short_description = 'Đang hoạt động'
    is_active.boolean = True
    
    def is_collecting(self, obj):
        """Hiển thị trạng thái thu thập lệnh"""
        return obj.is_collecting
    is_collecting.short_description = 'Đang thu thập lệnh'
    is_collecting.boolean = True
    
    def is_matching(self, obj):
        """Hiển thị trạng thái khớp lệnh"""
        return obj.is_matching
    is_matching.short_description = 'Đang khớp lệnh'
    is_matching.boolean = True


@admin.register(P2PTransaction)
class P2PTransactionAdmin(admin.ModelAdmin):
    """Admin cho quản lý giao dịch P2P"""
    
    list_display = [
        'transaction_id', 'transaction_type', 'buyer', 'seller', 'bet_slip',
        'quantity', 'price_per_unit', 'total_amount', 'status', 'created_at'
    ]
    
    list_filter = [
        'transaction_type', 'status', 'created_at'
    ]
    
    search_fields = [
        'transaction_id', 'buyer__username', 'seller__username', 'bet_slip__id'
    ]
    
    readonly_fields = [
        'transaction_id', 'is_completed', 'is_failed', 'processing_time',
        'created_at', 'updated_at', 'processed_at', 'completed_at'
    ]
    
    fieldsets = (
        ('Thông tin giao dịch', {
            'fields': ('transaction_id', 'transaction_type', 'status')
        }),
        ('Các bên tham gia', {
            'fields': ('buyer', 'seller')
        }),
        ('Thông tin phiếu cược', {
            'fields': ('bet_slip', 'quantity', 'ownership_percentage')
        }),
        ('Thông tin tài chính', {
            'fields': ('price_per_unit', 'total_amount', 'transaction_fee', 'net_amount_seller')
        }),
        ('Thông tin lệnh', {
            'fields': ('buy_order', 'sell_order')
        }),
        ('Trạng thái', {
            'fields': ('is_completed', 'is_failed', 'processing_time')
        }),
        ('Thời gian', {
            'fields': ('created_at', 'updated_at', 'processed_at', 'completed_at')
        }),
        ('Thông tin bổ sung', {
            'fields': ('notes', 'error_message')
        }),
    )
    
    def is_completed(self, obj):
        """Hiển thị trạng thái hoàn thành"""
        return obj.is_completed
    is_completed.short_description = 'Hoàn thành'
    is_completed.boolean = True
    
    def is_failed(self, obj):
        """Hiển thị trạng thái thất bại"""
        return obj.is_failed
    is_failed.short_description = 'Thất bại'
    is_failed.boolean = True
    
    def processing_time(self, obj):
        """Hiển thị thời gian xử lý"""
        if obj.processing_time:
            return f"{obj.processing_time.total_seconds():.1f} giây"
        return "N/A"
    processing_time.short_description = 'Thời gian xử lý'
