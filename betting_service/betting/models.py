from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal

class Sport(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=200)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='teams')
    country = models.CharField(max_length=100, blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)

    class Meta:
        unique_together = ('name', 'sport')

    def __str__(self):
        return f"{self.name} ({self.sport.name})"

class Match(models.Model):
    MATCH_STATUS_CHOICES = [
        ('SCHEDULED', 'Scheduled'),
        ('LIVE', 'Live'),
        ('FINISHED', 'Finished'),
        ('CANCELLED', 'Cancelled'),
        ('POSTPONED', 'Postponed'),
    ]

    STAKE_TYPE_CHOICES = [
        ('FREE', 'Free Stake (Cược miễn phí)'),
        ('FIXED', 'Fixed Stake (Cược cố định)'),
    ]

    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='matches')
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=MATCH_STATUS_CHOICES, default='SCHEDULED')
    score_home = models.IntegerField(blank=True, null=True)
    score_away = models.IntegerField(blank=True, null=True)
    current_minute = models.IntegerField(default=0) # For live matches
    
    # Stake type classification
    stake_type = models.CharField(max_length=10, choices=STAKE_TYPE_CHOICES, default='FREE', 
                                help_text='Loại hình sự kiện: Free stake hoặc Fixed stake')
    fixed_stake_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                          help_text='Giá trị cố định cho Fixed stake (chỉ áp dụng khi stake_type = FIXED)')
    
    # Legacy fields (keeping for backward compatibility)
    BET_TYPE_CATEGORY_CHOICES = [
        ('VARIABLE_STAKE', 'Variable Stake (Tỷ lệ biến động)'),
        ('FIXED_STAKE', 'Fixed Stake (Tỷ lệ cố định)'),
    ]
    bet_type_category = models.CharField(max_length=20, choices=BET_TYPE_CATEGORY_CHOICES, default='VARIABLE_STAKE')
    fixed_stake_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # Only for FIXED_STAKE matches
    
    # Add fields for live data, e.g., possession, shots on target, etc.

    class Meta:
        verbose_name_plural = 'Matches'
        ordering = ['start_time']

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name} ({self.sport.name})"

    def clean(self):
        """Validate that fixed_stake_value is provided when stake_type is FIXED"""
        from django.core.exceptions import ValidationError
        if self.stake_type == 'FIXED' and not self.fixed_stake_value:
            raise ValidationError('Fixed stake value is required when stake type is FIXED')
        if self.stake_type == 'FREE' and self.fixed_stake_value:
            raise ValidationError('Fixed stake value should not be set when stake type is FREE')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class BetType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Odd(models.Model):
    # Odds Type Choices
    ODDS_TYPE_CHOICES = [
        ('STATIC', 'Static (Tỷ lệ cố định)'),
        ('DYNAMIC', 'Dynamic (Tỷ lệ động)'),
        ('RISK_BASED', 'Risk-Based (Tỷ lệ dựa trên rủi ro)'),
    ]
    
    # Odds Status Choices
    ODDS_STATUS_CHOICES = [
        ('ACTIVE', 'Active (Hoạt động)'),
        ('SUSPENDED', 'Suspended (Tạm dừng)'),
        ('CLOSED', 'Closed (Đóng)'),
        ('LOCKED', 'Locked (Khóa)'),
    ]
    
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='odds')
    bet_type = models.ForeignKey(BetType, on_delete=models.CASCADE, related_name='odds')
    outcome = models.CharField(max_length=100) # e.g., Home Win, Away Win, Draw, Over 2.5, etc.
    value = models.DecimalField(max_digits=5, decimal_places=2) # e.g., 1.50, 2.00, 3.25
    
    # Enhanced fields for dynamic odds
    odds_type = models.CharField(max_length=20, choices=ODDS_TYPE_CHOICES, default='STATIC',
                                help_text='Loại tỷ lệ: Static, Dynamic, hoặc Risk-Based')
    odds_status = models.CharField(max_length=20, choices=ODDS_STATUS_CHOICES, default='ACTIVE',
                                  help_text='Trạng thái hiện tại của odds')
    
    # Risk-based odds fields
    base_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                    help_text='Giá trị cơ bản của odds (không thay đổi)')
    risk_multiplier = models.DecimalField(max_digits=5, decimal_places=2, default=1.00,
                                         help_text='Hệ số nhân rủi ro cho dynamic odds')
    liability_threshold = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                            help_text='Ngưỡng rủi ro tối đa cho phép')
    current_liability = models.DecimalField(max_digits=15, decimal_places=2, default=0.00,
                                          help_text='Rủi ro hiện tại đã tích lũy')
    
    # Dynamic odds configuration
    min_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                   help_text='Giá trị tối thiểu cho dynamic odds')
    max_value = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                   help_text='Giá trị tối đa cho dynamic odds')
    adjustment_step = models.DecimalField(max_digits=4, decimal_places=3, default=0.01,
                                        help_text='Bước điều chỉnh cho dynamic odds')
    
    # Metadata
    is_active = models.BooleanField(default=True)
    last_updated = models.DateTimeField(auto_now=True)
    last_risk_update = models.DateTimeField(null=True, blank=True,
                                           help_text='Thời điểm cập nhật rủi ro cuối cùng')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                  null=True, blank=True, related_name='created_odds')
    
    # Risk service integration
    risk_profile_id = models.CharField(max_length=255, blank=True, null=True,
                                      help_text='ID của risk profile từ Risk Management Service')
    auto_adjust_enabled = models.BooleanField(default=False,
                                             help_text='Bật/tắt tự động điều chỉnh odds theo rủi ro')

    class Meta:
        unique_together = ('match', 'bet_type', 'outcome')
        indexes = [
            models.Index(fields=['odds_type', 'odds_status']),
            models.Index(fields=['match', 'is_active']),
            models.Index(fields=['last_risk_update']),
        ]

    def __str__(self):
        return f"{self.match} - {self.bet_type.name}: {self.outcome} ({self.value})"
    
    def save(self, *args, **kwargs):
        # Auto-set base_value if not provided
        if not self.base_value:
            self.base_value = self.value
        
        # Validate dynamic odds constraints
        if self.odds_type in ['DYNAMIC', 'RISK_BASED']:
            if self.min_value and self.value < self.min_value:
                self.value = self.min_value
            if self.max_value and self.value > self.max_value:
                self.value = self.max_value
        
        super().save(*args, **kwargs)
    
    def adjust_for_risk(self, new_liability):
        """Điều chỉnh odds dựa trên rủi ro mới"""
        if self.odds_type != 'RISK_BASED' or not self.auto_adjust_enabled:
            return False
        
        self.current_liability = new_liability
        
        # Tính toán risk multiplier dựa trên liability
        if self.liability_threshold and new_liability > self.liability_threshold:
            # Tăng odds để giảm rủi ro
            risk_ratio = new_liability / self.liability_threshold
            self.risk_multiplier = min(risk_ratio, 2.0)  # Giới hạn tối đa 2x
            
            # Tính odds mới
            new_value = self.base_value * self.risk_multiplier
            
            # Áp dụng giới hạn min/max
            if self.min_value and new_value < self.min_value:
                new_value = self.min_value
            if self.max_value and new_value > self.max_value:
                new_value = self.max_value
            
            # Chỉ cập nhật nếu có thay đổi đáng kể
            if abs(new_value - self.value) >= self.adjustment_step:
                old_value = self.value
                self.value = new_value
                self.last_risk_update = timezone.now()
                
                # Tạo history record
                OddsHistory.objects.create(
                    odd=self,
                    old_value=old_value,
                    new_value=new_value,
                    change_reason='RISK_ADJUSTMENT',
                    risk_liability=new_liability,
                    risk_multiplier=self.risk_multiplier
                )
                
                return True
        
        return False
    
    def suspend_odds(self, reason="Odds suspended"):
        """Tạm dừng odds"""
        if self.odds_status != 'SUSPENDED':
            old_status = self.odds_status
            self.odds_status = 'SUSPENDED'
            self.save()
            
            # Log status change
            OddsHistory.objects.create(
                odd=self,
                old_value=self.value,
                new_value=self.value,
                change_reason='STATUS_CHANGE',
                additional_data={'old_status': old_status, 'new_status': 'SUSPENDED', 'reason': reason}
            )
    
    def resume_odds(self):
        """Khôi phục odds"""
        if self.odds_status == 'SUSPENDED':
            old_status = self.odds_status
            self.odds_status = 'ACTIVE'
            self.save()
            
            # Log status change
            OddsHistory.objects.create(
                odd=self,
                old_value=self.value,
                new_value=self.value,
                change_reason='STATUS_CHANGE',
                additional_data={'old_status': old_status, 'new_status': 'ACTIVE', 'reason': 'Odds resumed'}
            )

class OddsHistory(models.Model):
    """Model lưu lịch sử thay đổi odds"""
    
    CHANGE_REASON_CHOICES = [
        ('MANUAL_ADJUSTMENT', 'Manual Adjustment (Điều chỉnh thủ công)'),
        ('RISK_ADJUSTMENT', 'Risk Adjustment (Điều chỉnh theo rủi ro)'),
        ('MARKET_CHANGE', 'Market Change (Thay đổi thị trường)'),
        ('LIQUIDITY_ADJUSTMENT', 'Liquidity Adjustment (Điều chỉnh thanh khoản)'),
        ('STATUS_CHANGE', 'Status Change (Thay đổi trạng thái)'),
        ('SYSTEM_UPDATE', 'System Update (Cập nhật hệ thống)'),
        ('PROMOTION_IMPACT', 'Promotion Impact (Tác động khuyến mãi)'),
    ]
    
    odd = models.ForeignKey(Odd, on_delete=models.CASCADE, related_name='history')
    old_value = models.DecimalField(max_digits=5, decimal_places=2, help_text='Giá trị odds cũ')
    new_value = models.DecimalField(max_digits=5, decimal_places=2, help_text='Giá trị odds mới')
    change_reason = models.CharField(max_length=50, choices=CHANGE_REASON_CHOICES, help_text='Lý do thay đổi')
    
    # Risk-related fields
    risk_liability = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True,
                                        help_text='Rủi ro tại thời điểm thay đổi')
    risk_multiplier = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                         help_text='Hệ số rủi ro tại thời điểm thay đổi')
    
    # Additional data for complex changes
    additional_data = models.JSONField(default=dict, blank=True,
                                      help_text='Dữ liệu bổ sung (status changes, market data, etc.)')
    
    # Metadata
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                  null=True, blank=True, related_name='odds_changes')
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Risk service integration
    risk_profile_id = models.CharField(max_length=255, blank=True, null=True,
                                      help_text='ID của risk profile từ Risk Management Service')
    risk_alert_id = models.CharField(max_length=255, blank=True, null=True,
                                    help_text='ID của risk alert nếu có')

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['odd', 'timestamp']),
            models.Index(fields=['change_reason', 'timestamp']),
            models.Index(fields=['risk_liability']),
        ]
        verbose_name_plural = 'Odds History'

    def __str__(self):
        return f"{self.odd} - {self.old_value} → {self.new_value} ({self.change_reason})"
    
    @property
    def change_percentage(self):
        """Tính phần trăm thay đổi"""
        if self.old_value > 0:
            return ((self.new_value - self.old_value) / self.old_value) * 100
        return 0
    
    @property
    def is_significant_change(self):
        """Kiểm tra xem thay đổi có đáng kể không (>5%)"""
        return abs(self.change_percentage) > 5

class BetSlip(models.Model):
    BET_TYPE_CHOICES = [
        ('SINGLE', 'Single Bet (Cược đơn)'),
        ('MULTIPLE', 'Multiple Bets (Cược nhiều)'),
        ('PARLAY', 'Parlay (Cược xiên)'),
        ('SYSTEM', 'System Bet (Cược hệ thống)'),
    ]
    
    BET_STATUS_CHOICES = [
        ('PENDING', 'Pending (Chờ xử lý)'),
        ('CONFIRMED', 'Confirmed (Đã xác nhận)'),
        ('CANCELLED', 'Cancelled (Đã hủy)'),
        ('SETTLED', 'Settled (Đã thanh toán)'),
        ('CASHED_OUT', 'Cashed Out (Đã rút tiền)'),
        ('CASHING_OUT', 'Cashing Out (Đang xử lý rút tiền)'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bet_slips')
    created_at = models.DateTimeField(auto_now_add=True)
    total_stake = models.DecimalField(max_digits=10, decimal_places=2)
    potential_payout = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_settled = models.BooleanField(default=False)
    is_won = models.BooleanField(blank=True, null=True)
    # promotion = models.ForeignKey("promotions.Promotion", on_delete=models.SET_NULL, blank=True, null=True)
    
    # Enhanced Cash Out fields
    cash_out_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                       help_text='Giá trị Cash Out thực tế người chơi nhận được')
    cash_out_fair_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                            help_text='Giá trị công bằng trước khi trừ phí')
    cash_out_fee_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True,
                                            help_text='Số tiền phí Cash Out')
    cash_out_fee_percentage = models.DecimalField(max_digits=5, decimal_places=4, null=True, blank=True,
                                                help_text='Tỷ lệ phí Cash Out (0.05 = 5%)')
    is_cash_out_available = models.BooleanField(default=False,
                                               help_text='Có thể Cash Out hay không')
    cash_out_at = models.DateTimeField(null=True, blank=True,
                                     help_text='Thời điểm thực hiện Cash Out')
    cash_out_requested_at = models.DateTimeField(null=True, blank=True,
                                               help_text='Thời điểm yêu cầu Cash Out')
    
    # Cash Out configuration
    cash_out_enabled = models.BooleanField(default=True,
                                          help_text='Tính năng Cash Out có được bật cho phiếu cược này không')
    cash_out_before_match = models.BooleanField(default=False,
                                              help_text='Cho phép Cash Out trước khi trận đấu bắt đầu')
    
    # New fields for enhanced bet management
    bet_type = models.CharField(max_length=20, choices=BET_TYPE_CHOICES, default='SINGLE')
    bet_status = models.CharField(max_length=20, choices=BET_STATUS_CHOICES, default='PENDING')
    
    # Saga integration fields
    saga_transaction_id = models.CharField(max_length=255, blank=True, null=True, 
                                         help_text='ID của saga transaction để theo dõi quá trình xử lý')
    wallet_transaction_id = models.CharField(max_length=255, blank=True, null=True,
                                           help_text='ID của wallet transaction')
    
    # Timestamps for status tracking
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    settled_at = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    # Auto Order Management (Chốt Lời & Cắt Lỗ tự động)
    AUTO_ORDER_STATUS_CHOICES = [
        ('INACTIVE', 'Inactive (Không hoạt động)'),
        ('ACTIVE', 'Active (Đang hoạt động)'),
        ('TRIGGERED', 'Triggered (Đã kích hoạt)'),
        ('COMPLETED', 'Completed (Đã hoàn thành)'),
        ('CANCELLED', 'Cancelled (Đã hủy)'),
        ('SUSPENDED', 'Suspended (Tạm dừng)'),
    ]
    
    take_profit_threshold = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='Ngưỡng chốt lời - Tự động Cash Out khi đạt mức lợi nhuận này'
    )
    stop_loss_threshold = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='Ngưỡng cắt lỗ - Tự động Cash Out khi giảm xuống mức thua lỗ này'
    )
    auto_order_status = models.CharField(
        max_length=20, 
        choices=AUTO_ORDER_STATUS_CHOICES, 
        default='INACTIVE',
        help_text='Trạng thái lệnh tự động'
    )
    auto_order_created_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='Thời điểm tạo lệnh tự động'
    )
    auto_order_triggered_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text='Thời điểm lệnh tự động được kích hoạt'
    )
    auto_order_reason = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='Lý do kích hoạt lệnh tự động (TAKE_PROFIT/STOP_LOSS)'
    )
    auto_order_enabled = models.BooleanField(
        default=False,
        help_text='Tính năng lệnh tự động có được bật cho phiếu cược này không'
    )

    class Meta:
        indexes = [
            models.Index(fields=['user', 'bet_status']),
            models.Index(fields=['is_cash_out_available']),
            models.Index(fields=['cash_out_enabled']),
            models.Index(fields=['created_at']),
            models.Index(fields=['auto_order_status']),
            models.Index(fields=['auto_order_enabled']),
            models.Index(fields=['take_profit_threshold']),
            models.Index(fields=['stop_loss_threshold']),
        ]

    def __str__(self):
        return f"BetSlip #{self.id} by {self.user.username} ({self.bet_status})"
    
    @property
    def can_cash_out(self):
        """Kiểm tra xem phiếu cược có thể Cash Out hay không"""
        if not self.cash_out_enabled:
            return False
        
        if self.bet_status not in ['CONFIRMED']:
            return False
        
        if self.is_settled:
            return False
        
        # Kiểm tra xem có phải cược xâu đã thua chưa
        if self.bet_type == 'PARLAY':
            for selection in self.selections.all():
                if selection.is_lost:
                    return False
        
        return True
    
    @property
    def can_cash_out_before_match(self):
        """Kiểm tra xem có thể Cash Out trước khi trận đấu bắt đầu không"""
        if not self.cash_out_before_match:
            return False
        
        # Kiểm tra xem trận đấu đã bắt đầu chưa
        for selection in self.selections.all():
            match = selection.odd.match
            if match.status in ['LIVE', 'FINISHED', 'CANCELLED']:
                return False
        
        return True
    
    @property
    def cash_out_profit_loss(self):
        """Tính lãi/lỗ từ Cash Out"""
        if not self.cash_out_value:
            return None
        return self.cash_out_value - self.total_stake
    
    def confirm_bet(self):
        """Xác nhận bet sau khi trừ tiền thành công"""
        self.bet_status = 'CONFIRMED'
        self.confirmed_at = timezone.now()
        self.save()
    
    def cancel_bet(self, reason=""):
        """Hủy bet khi có lỗi"""
        self.bet_status = 'CANCELLED'
        self.cancelled_at = timezone.now()
        if reason:
            self.error_message = reason
        self.save()
    
    def settle_bet(self, is_won):
        """Thanh toán bet"""
        self.is_settled = True
        self.is_won = is_won
        self.bet_status = 'SETTLED'
        self.settled_at = timezone.now()
        self.save()
    
    def request_cash_out(self):
        """Yêu cầu Cash Out"""
        if not self.can_cash_out:
            raise ValueError("Không thể Cash Out phiếu cược này")
        
        self.cash_out_requested_at = timezone.now()
        self.save()
    
    def process_cash_out(self, cash_out_value, fair_value, fee_amount, fee_percentage):
        """Xử lý Cash Out thành công"""
        self.cash_out_value = cash_out_value
        self.cash_out_fair_value = fair_value
        self.cash_out_fee_amount = fee_amount
        self.cash_out_fee_percentage = fee_percentage
        self.cash_out_at = timezone.now()
        self.bet_status = 'CASHED_OUT'
        self.is_settled = True
        self.is_cash_out_available = False
        self.save()
    
    def cancel_cash_out(self):
        """Hủy yêu cầu Cash Out"""
        self.cash_out_requested_at = None
        self.save()
    
    # Auto Order Management Methods
    def setup_auto_order(self, take_profit_threshold=None, stop_loss_threshold=None):
        """Thiết lập lệnh tự động (Chốt Lời & Cắt Lỗ)"""
        if not self.can_cash_out:
            raise ValueError("Phiếu cược không thể thiết lập lệnh tự động")
        
        if not take_profit_threshold and not stop_loss_threshold:
            raise ValueError("Phải có ít nhất một ngưỡng (chốt lời hoặc cắt lỗ)")
        
        self.take_profit_threshold = take_profit_threshold
        self.stop_loss_threshold = stop_loss_threshold
        self.auto_order_status = 'ACTIVE'
        self.auto_order_enabled = True
        self.auto_order_created_at = timezone.now()
        self.save()
        
        return True
    
    def cancel_auto_order(self):
        """Hủy lệnh tự động"""
        self.auto_order_status = 'CANCELLED'
        self.auto_order_enabled = False
        self.save()
        
        return True
    
    def suspend_auto_order(self):
        """Tạm dừng lệnh tự động (khi thị trường bị khóa)"""
        if self.auto_order_status == 'ACTIVE':
            self.auto_order_status = 'SUSPENDED'
            self.save()
        
        return True
    
    def resume_auto_order(self):
        """Khôi phục lệnh tự động (khi thị trường mở lại)"""
        if self.auto_order_status == 'SUSPENDED':
            self.auto_order_status = 'ACTIVE'
            self.save()
        
        return True
    
    def trigger_auto_order(self, reason):
        """Kích hoạt lệnh tự động"""
        self.auto_order_status = 'TRIGGERED'
        self.auto_order_triggered_at = timezone.now()
        self.auto_order_reason = reason
        self.save()
        
        return True
    
    def complete_auto_order(self):
        """Hoàn thành lệnh tự động"""
        self.auto_order_status = 'COMPLETED'
        self.auto_order_enabled = False
        self.save()
        
        return True
    
    @property
    def has_active_auto_order(self):
        """Kiểm tra xem có lệnh tự động đang hoạt động không"""
        return self.auto_order_enabled and self.auto_order_status in ['ACTIVE', 'SUSPENDED']
    
    @property
    def can_setup_auto_order(self):
        """Kiểm tra xem có thể thiết lập lệnh tự động không"""
        return (self.can_cash_out and 
                not self.has_active_auto_order and 
                self.bet_status == 'CONFIRMED')


class BetSelection(models.Model):
    bet_slip = models.ForeignKey(BetSlip, on_delete=models.CASCADE, related_name="selections")
    odd = models.ForeignKey(Odd, on_delete=models.CASCADE)
    selected_value = models.DecimalField(max_digits=5, decimal_places=2) # Value of the odd when selected
    
    # New field to store odds snapshot at placement time
    odds_at_placement = models.DecimalField(max_digits=5, decimal_places=2, 
                                          help_text='Snapshot của odds tại thời điểm đặt cược')
    placement_timestamp = models.DateTimeField(auto_now_add=True)
    
    # Cash Out support fields
    live_odds_at_cashout = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True,
                                             help_text='Live odds tại thời điểm Cash Out')
    cashout_timestamp = models.DateTimeField(null=True, blank=True,
                                           help_text='Thời điểm Cash Out được thực hiện')
    
    # Selection status tracking
    SELECTION_STATUS_CHOICES = [
        ('PENDING', 'Pending (Chờ xử lý)'),
        ('WINNING', 'Winning (Đang thắng)'),
        ('LOSING', 'Losing (Đã thua)'),
        ('SETTLED', 'Settled (Đã thanh toán)'),
    ]
    selection_status = models.CharField(max_length=20, choices=SELECTION_STATUS_CHOICES, default='PENDING')
    
    def __str__(self):
        return f"{self.bet_slip} - {self.odd.match} - {self.odd.outcome}"
    
    @property
    def is_won(self):
        """Kiểm tra xem selection này có thắng hay không"""
        if self.selection_status == 'SETTLED':
            return self.selection_status == 'WINNING'
        
        # Logic kiểm tra dựa trên match status và score
        match = self.odd.match
        if match.status == 'FINISHED':
            # Đây là logic đơn giản, cần được mở rộng dựa trên bet type
            return self._check_selection_result()
        return None
    
    @property
    def is_lost(self):
        """Kiểm tra xem selection này có thua hay không"""
        if self.selection_status == 'SETTLED':
            return self.selection_status == 'LOSING'
        
        match = self.odd.match
        if match.status == 'FINISHED':
            result = self._check_selection_result()
            return result is not None and not result
        return None
    
    def _check_selection_result(self):
        """Kiểm tra kết quả của selection dựa trên bet type và match result"""
        # Đây là logic cơ bản, cần được mở rộng dựa trên bet type cụ thể
        # Ví dụ: Over/Under, Handicap, etc.
        match = self.odd.match
        
        # Kiểm tra cơ bản cho 1X2
        if self.odd.bet_type.name in ['Match Winner', '1X2']:
            if self.odd.outcome == 'Home Win':
                return match.score_home > match.score_away
            elif self.odd.outcome == 'Away Win':
                return match.score_away > match.score_home
            elif self.odd.outcome == 'Draw':
                return match.score_home == match.score_away
        
        # Cần thêm logic cho các bet type khác
        return None
    
    def update_live_odds(self, live_odds):
        """Cập nhật live odds cho Cash Out"""
        self.live_odds_at_cashout = live_odds
        self.cashout_timestamp = timezone.now()
        self.save()
    
    def save(self, *args, **kwargs):
        # Tự động lưu odds snapshot khi tạo mới
        if not self.odds_at_placement:
            self.odds_at_placement = self.odd.value
        super().save(*args, **kwargs)

class BetSlipPurchase(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sold_bet_slips")
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bought_bet_slips", blank=True, null=True)
    bet_slip = models.OneToOneField(BetSlip, on_delete=models.CASCADE, related_name="purchase_offer")
    price = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    purchased_at = models.DateTimeField(blank=True, null=True)
    is_p2p_offer = models.BooleanField(default=False) # Indicates if this is a P2P offer
    is_fractional = models.BooleanField(default=False) # Indicates if the bet slip can be bought in fractions
    available_fractions = models.IntegerField(null=True, blank=True) # Number of fractions available for purchase
    total_fractions = models.IntegerField(null=True, blank=True) # Total number of fractions for the bet slip


    def __str__(self):
        return f"Purchase offer for BetSlip #{self.bet_slip.id} by {self.seller.username}"



class ResponsibleGamingPolicy(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="responsible_gaming_policy")
    deposit_limit_daily = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    deposit_limit_weekly = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    deposit_limit_monthly = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    loss_limit_daily = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    loss_limit_weekly = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    loss_limit_monthly = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    session_limit_minutes = models.IntegerField(null=True, blank=True)
    self_exclusion_until = models.DateTimeField(null=True, blank=True)
    cool_off_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Responsible Gaming Policy for {self.user.username}"

class UserActivityLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activity_logs")
    activity_type = models.CharField(max_length=100) # e.g., login, logout, bet_placed, deposit, withdrawal
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.user.username} - {self.activity_type} at {self.timestamp}"


class CashOutConfiguration(models.Model):
    """Cấu hình phí Cash Out cho từng nhà cái"""
    
    BOOKMAKER_TYPE_CHOICES = [
        ('SYSTEM', 'System Bookmaker (Nhà cái hệ thống)'),
        ('COMMUNITY', 'Community Bookmaker (Nhà cái cộng đồng)'),
        ('INDIVIDUAL', 'Individual User (Người dùng cá nhân)'),
        ('GROUP', 'Group Users (Nhóm người dùng)'),
    ]
    
    # Đối tượng áp dụng cấu hình
    bookmaker_type = models.CharField(max_length=20, choices=BOOKMAKER_TYPE_CHOICES)
    bookmaker_id = models.CharField(max_length=255, 
                                  help_text='ID của nhà cái (user_id, group_id, hoặc "system")')
    
    # Cấu hình phí Cash Out - CÓ THỂ ĐỂ TRỐNG để sử dụng margin của sự kiện
    cash_out_fee_percentage = models.DecimalField(
        max_digits=5, decimal_places=4, null=True, blank=True,
        help_text='Tỷ lệ phí Cash Out cụ thể (để trống để sử dụng margin của sự kiện)'
    )
    
    # Cấu hình tính năng
    cash_out_enabled = models.BooleanField(default=True,
                                          help_text='Bật/tắt tính năng Cash Out')
    cash_out_before_match = models.BooleanField(default=False,
                                              help_text='Cho phép Cash Out trước khi trận đấu bắt đầu')
    
    # Giới hạn và ràng buộc
    min_cash_out_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Số tiền Cash Out tối thiểu'
    )
    max_cash_out_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text='Số tiền Cash Out tối đa'
    )
    
    # Thời gian áp dụng
    valid_from = models.DateTimeField(default=timezone.now,
                                    help_text='Thời điểm bắt đầu áp dụng cấu hình')
    valid_until = models.DateTimeField(null=True, blank=True,
                                     help_text='Thời điểm kết thúc áp dụng cấu hình')
    
    # Metadata
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                                  null=True, blank=True, related_name='created_cashout_configs')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('bookmaker_type', 'bookmaker_id')
        indexes = [
            models.Index(fields=['bookmaker_type', 'bookmaker_id']),
            models.Index(fields=['cash_out_enabled']),
            models.Index(fields=['valid_from', 'valid_until']),
        ]
        verbose_name = 'Cash Out Configuration'
        verbose_name_plural = 'Cash Out Configurations'
    
    def __str__(self):
        return f"Cash Out Config for {self.get_bookmaker_type_display()} - {self.bookmaker_id}"
    
    @property
    def is_valid(self):
        """Kiểm tra xem cấu hình có còn hiệu lực không"""
        now = timezone.now()
        if not self.is_active:
            return False
        
        if self.valid_from > now:
            return False
        
        if self.valid_until and self.valid_until < now:
            return False
        
        return True
    
    def get_cash_out_fee(self, stake_amount, event_margin=None):
        """
        Tính phí Cash Out theo logic đúng:
        - Nhà cái hệ thống: sử dụng margin của sự kiện nếu không có phí cụ thể
        - Nhà cái cá nhân/nhóm: phí tối thiểu 0%
        """
        if not self.is_valid or not self.cash_out_enabled:
            return Decimal('0.00')
        
        # Nếu có phí cấu hình cụ thể, sử dụng
        if self.cash_out_fee_percentage is not None:
            fee_amount = stake_amount * self.cash_out_fee_percentage
        else:
            # Sử dụng margin của sự kiện cho nhà cái hệ thống
            if self.bookmaker_type == 'SYSTEM' and event_margin:
                fee_amount = stake_amount * event_margin
            else:
                # Nhà cái cá nhân/nhóm: phí tối thiểu 0%
                fee_amount = Decimal('0.00')
        
        # Áp dụng giới hạn min/max nếu có
        if self.min_cash_out_amount and fee_amount < self.min_cash_out_amount:
            fee_amount = self.min_cash_out_amount
        elif self.max_cash_out_amount and fee_amount > self.max_cash_out_amount:
            fee_amount = self.max_cash_out_amount
        
        return fee_amount
    
    def get_fee_percentage_for_display(self, event_margin=None):
        """Lấy tỷ lệ phí để hiển thị (bao gồm cả margin của sự kiện)"""
        if self.cash_out_fee_percentage is not None:
            return self.cash_out_fee_percentage
        elif self.bookmaker_type == 'SYSTEM' and event_margin:
            return event_margin
        else:
            return Decimal('0.00')
    
    @classmethod
    def get_config_for_bookmaker(cls, bookmaker_type, bookmaker_id):
        """Lấy cấu hình Cash Out cho một nhà cái cụ thể"""
        try:
            config = cls.objects.get(
                bookmaker_type=bookmaker_type,
                bookmaker_id=bookmaker_id,
                is_active=True
            )
            
            if config.is_valid:
                return config
        except cls.DoesNotExist:
            pass
        
        # Trả về cấu hình mặc định nếu không tìm thấy
        return cls._get_default_config(bookmaker_type)
    
    @classmethod
    def _get_default_config(cls, bookmaker_type):
        """Lấy cấu hình mặc định cho từng loại nhà cái"""
        if bookmaker_type == 'SYSTEM':
            # Nhà cái hệ thống: không có phí cụ thể, sẽ sử dụng margin của sự kiện
            return cls(
                bookmaker_type=bookmaker_type,
                bookmaker_id='system',
                cash_out_fee_percentage=None,  # Để trống để sử dụng margin của sự kiện
                cash_out_enabled=True,
                cash_out_before_match=False
            )
        elif bookmaker_type in ['COMMUNITY', 'INDIVIDUAL', 'GROUP']:
            # Nhà cái cộng đồng/cá nhân: phí tối thiểu 0%
            return cls(
                bookmaker_type=bookmaker_type,
                bookmaker_id='default',
                cash_out_fee_percentage=Decimal('0.00'),  # 0% mặc định
                cash_out_enabled=True,
                cash_out_before_match=False
            )
        
        return None

    def get_cash_out_eligibility(self, bet_slip):
        """Kiểm tra tính đủ điều kiện Cash Out của một phiếu cược"""
        eligibility = {
            'can_cash_out': bet_slip.can_cash_out,
            'can_cash_out_before_match': bet_slip.can_cash_out_before_match,
            'reasons': []
        }
        
        if not bet_slip.cash_out_enabled:
            eligibility['reasons'].append('Tính năng Cash Out bị tắt cho phiếu cược này')
        
        if bet_slip.bet_status not in ['CONFIRMED']:
            eligibility['reasons'].append(f'Trạng thái phiếu cược không phù hợp: {bet_slip.bet_status}')
        
        if bet_slip.is_settled:
            eligibility['reasons'].append('Phiếu cược đã được thanh toán')
        
        # Kiểm tra cược xâu
        if bet_slip.bet_type == 'PARLAY':
            for selection in bet_slip.selections.all():
                if selection.is_lost:
                    eligibility['reasons'].append('Cược xâu đã thua, không thể Cash Out')
                    break
        
        # Thông tin bổ sung
        eligibility.update({
            'cash_out_enabled': bet_slip.cash_out_enabled,
            'cash_out_before_match': bet_slip.cash_out_before_match,
            'bet_status': bet_slip.bet_status,
            'bet_type': bet_slip.bet_type
        })
        
        return eligibility


class UserStatistics(models.Model):
    """Thống kê tổng hợp của người dùng"""
    
    PERIOD_CHOICES = [
        ('DAILY', 'Daily (Hàng ngày)'),
        ('WEEKLY', 'Weekly (Hàng tuần)'),
        ('BIWEEKLY', 'Biweekly (2 tuần)'),
        ('MONTHLY', 'Monthly (Hàng tháng)'),
        ('QUARTERLY', 'Quarterly (Theo quý)'),
        ('YEARLY', 'Yearly (Hàng năm)'),
        ('ALL_TIME', 'All Time (Tất cả thời gian)'),
    ]
    
    # Thông tin cơ bản
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                            related_name='statistics')
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='ALL_TIME')
    period_start = models.DateTimeField(help_text='Thời điểm bắt đầu kỳ thống kê')
    period_end = models.DateTimeField(help_text='Thời điểm kết thúc kỳ thống kê')
    
    # Thống kê cơ bản
    total_bets = models.IntegerField(default=0, help_text='Tổng số phiếu cược')
    total_wins = models.IntegerField(default=0, help_text='Tổng số phiếu thắng')
    total_losses = models.IntegerField(default=0, help_text='Tổng số phiếu thua')
    total_draws = models.IntegerField(default=0, help_text='Tổng số phiếu hòa')
    
    # Thống kê tài chính
    total_stake = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                    help_text='Tổng số tiền cược')
    total_return = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     help_text='Tổng số tiền nhận về')
    total_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     help_text='Tổng lãi/lỗ')
    total_fees = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                   help_text='Tổng phí giao dịch')
    
    # Tỷ lệ và hiệu suất
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                 help_text='Tỷ lệ thắng (%)')
    roi = models.DecimalField(max_digits=8, decimal_places=4, default=0,
                             help_text='Return on Investment (%)')
    average_odds = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                     help_text='Tỷ lệ cược trung bình')
    average_bet_size = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                         help_text='Số tiền cược trung bình')
    
    # Chuỗi thắng/thua
    best_win_streak = models.IntegerField(default=0, help_text='Chuỗi thắng dài nhất')
    current_win_streak = models.IntegerField(default=0, help_text='Chuỗi thắng hiện tại')
    best_loss_streak = models.IntegerField(default=0, help_text='Chuỗi thua dài nhất')
    current_loss_streak = models.IntegerField(default=0, help_text='Chuỗi thua hiện tại')
    
    # Thống kê theo loại cược
    single_bets = models.IntegerField(default=0, help_text='Số phiếu cược đơn')
    multiple_bets = models.IntegerField(default=0, help_text='Số phiếu cược kép')
    system_bets = models.IntegerField(default=0, help_text='Số phiếu cược hệ thống')
    
    # Thống kê theo môn thể thao
    football_bets = models.IntegerField(default=0, help_text='Số phiếu cược bóng đá')
    basketball_bets = models.IntegerField(default=0, help_text='Số phiếu cược bóng rổ')
    tennis_bets = models.IntegerField(default=0, help_text='Số phiếu cược tennis')
    other_sports_bets = models.IntegerField(default=0, help_text='Số phiếu cược môn khác')
    
    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'user_statistics'
        ordering = ['-period_start', '-total_profit']
        unique_together = ('user', 'period', 'period_start')
        indexes = [
            models.Index(fields=['user', 'period']),
            models.Index(fields=['period', 'total_profit']),
            models.Index(fields=['user', 'win_rate']),
            models.Index(fields=['period_start', 'period_end']),
        ]
        verbose_name = 'User Statistics'
        verbose_name_plural = 'User Statistics'
    
    def __str__(self):
        return f"{self.user.email} - {self.get_period_display()} ({self.period_start.date()})"
    
    def calculate_win_rate(self):
        """Tính tỷ lệ thắng"""
        if self.total_bets > 0:
            return (self.total_wins / self.total_bets) * 100
        return 0
    
    def calculate_roi(self):
        """Tính Return on Investment"""
        if self.total_stake > 0:
            return ((self.total_return - self.total_stake) / self.total_stake) * 100
        return 0
    
    def calculate_average_bet_size(self):
        """Tính số tiền cược trung bình"""
        if self.total_bets > 0:
            return self.total_stake / self.total_bets
        return 0
    
    def save(self, *args, **kwargs):
        """Tự động tính toán các giá trị trước khi lưu"""
        self.win_rate = self.calculate_win_rate()
        self.roi = self.calculate_roi()
        self.average_bet_size = self.calculate_average_bet_size()
        super().save(*args, **kwargs)


class Leaderboard(models.Model):
    """Bảng xếp hạng người chơi"""
    
    PERIOD_CHOICES = [
        ('DAILY', 'Daily (Hàng ngày)'),
        ('WEEKLY', 'Weekly (Hàng tuần)'),
        ('BIWEEKLY', 'Biweekly (2 tuần)'),
        ('MONTHLY', 'Monthly (Hàng tháng)'),
        ('QUARTERLY', 'Quarterly (Theo quý)'),
        ('YEARLY', 'Yearly (Hàng năm)'),
        ('ALL_TIME', 'All Time (Tất cả thời gian)'),
    ]
    
    CATEGORY_CHOICES = [
        ('OVERALL', 'Overall (Tổng thể)'),
        ('PROFIT', 'Profit (Lãi cao nhất)'),
        ('WIN_RATE', 'Win Rate (Tỷ lệ thắng cao nhất)'),
        ('VOLUME', 'Volume (Khối lượng cược cao nhất)'),
        ('STREAK', 'Streak (Chuỗi thắng dài nhất)'),
        ('ROI', 'ROI (Return on Investment cao nhất)'),
    ]
    
    # Thông tin cơ bản
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='WEEKLY')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='OVERALL')
    period_start = models.DateTimeField(help_text='Thời điểm bắt đầu kỳ xếp hạng')
    period_end = models.DateTimeField(help_text='Thời điểm kết thúc kỳ xếp hạng')
    
    # Thông tin người dùng
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            related_name='leaderboard_entries')
    
    # Xếp hạng và điểm số
    rank = models.IntegerField(help_text='Thứ hạng trong bảng xếp hạng')
    points = models.IntegerField(default=0, help_text='Điểm số để xếp hạng')
    
    # Các chỉ số xếp hạng
    total_profit = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     help_text='Tổng lãi/lỗ')
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                 help_text='Tỷ lệ thắng (%)')
    total_bets = models.IntegerField(default=0, help_text='Tổng số phiếu cược')
    total_stake = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                    help_text='Tổng số tiền cược')
    win_streak = models.IntegerField(default=0, help_text='Chuỗi thắng hiện tại')
    roi = models.DecimalField(max_digits=8, decimal_places=4, default=0,
                             help_text='Return on Investment (%)')
    
    # Thông tin bổ sung
    is_featured = models.BooleanField(default=False, help_text='Có được highlight không')
    featured_reason = models.TextField(blank=True, null=True, 
                                     help_text='Lý do được highlight')
    
    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'leaderboards'
        ordering = ['period', 'category', 'rank']
        unique_together = ('period', 'category', 'user', 'period_start')
        indexes = [
            models.Index(fields=['period', 'category', 'rank']),
            models.Index(fields=['user', 'period']),
            models.Index(fields=['period_start', 'period_end']),
            models.Index(fields=['points']),
        ]
        verbose_name = 'Leaderboard Entry'
        verbose_name_plural = 'Leaderboard Entries'
    
    def __str__(self):
        return f"{self.get_period_display()} - {self.get_category_display()} - #{self.rank} {self.user.email}"
    
    def get_rank_display(self):
        """Hiển thị thứ hạng với icon"""
        if self.rank == 1:
            return "🥇 #1"
        elif self.rank == 2:
            return "🥈 #2"
        elif self.rank == 3:
            return "🥉 #3"
        else:
            return f"#{self.rank}"


class BettingStatistics(models.Model):
    """Thống kê tổng hợp về cược"""
    
    PERIOD_CHOICES = [
        ('DAILY', 'Daily (Hàng ngày)'),
        ('WEEKLY', 'Weekly (Hàng tuần)'),
        ('BIWEEKLY', 'Biweekly (2 tuần)'),
        ('MONTHLY', 'Monthly (Hàng tháng)'),
        ('QUARTERLY', 'Quarterly (Theo quý)'),
        ('YEARLY', 'Yearly (Hàng năm)'),
        ('ALL_TIME', 'All Time (Tất cả thời gian)'),
    ]
    
    # Thông tin cơ bản
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES, default='DAILY')
    period_start = models.DateTimeField(help_text='Thời điểm bắt đầu kỳ thống kê')
    period_end = models.DateTimeField(help_text='Thời điểm kết thúc kỳ thống kê')
    
    # Thống kê tổng quan
    total_bets_placed = models.IntegerField(default=0, help_text='Tổng số phiếu cược')
    total_unique_users = models.IntegerField(default=0, help_text='Tổng số người dùng đặt cược')
    total_matches = models.IntegerField(default=0, help_text='Tổng số trận đấu có cược')
    
    # Thống kê tài chính
    total_stake_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0,
                                           help_text='Tổng số tiền cược')
    total_return_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0,
                                            help_text='Tổng số tiền trả về')
    total_profit = models.DecimalField(max_digits=20, decimal_places=2, default=0,
                                     help_text='Tổng lãi/lỗ của nhà cái')
    house_edge = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                   help_text='Biên lợi nhuận của nhà cái (%)')
    
    # Thống kê theo loại cược
    single_bets_count = models.IntegerField(default=0, help_text='Số phiếu cược đơn')
    multiple_bets_count = models.IntegerField(default=0, help_text='Số phiếu cược kép')
    system_bets_count = models.IntegerField(default=0, help_text='Số phiếu cược hệ thống')
    
    # Thống kê theo môn thể thao
    football_bets = models.IntegerField(default=0, help_text='Số phiếu cược bóng đá')
    basketball_bets = models.IntegerField(default=0, help_text='Số phiếu cược bóng rổ')
    tennis_bets = models.IntegerField(default=0, help_text='Số phiếu cược tennis')
    other_sports_bets = models.IntegerField(default=0, help_text='Số phiếu cược môn khác')
    
    # Thống kê theo loại stake
    free_stake_bets = models.IntegerField(default=0, help_text='Số phiếu cược Free Stake')
    fixed_stake_bets = models.IntegerField(default=0, help_text='Số phiếu cược Fixed Stake')
    
    # Thống kê Cash Out
    total_cashout_requests = models.IntegerField(default=0, help_text='Tổng số yêu cầu Cash Out')
    total_cashout_amount = models.DecimalField(max_digits=20, decimal_places=2, default=0,
                                             help_text='Tổng số tiền Cash Out')
    cashout_success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                             help_text='Tỷ lệ thành công Cash Out (%)')
    
    # Thống kê hiệu suất
    average_bet_size = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                         help_text='Số tiền cược trung bình')
    average_odds = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                     help_text='Tỷ lệ cược trung bình')
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                 help_text='Tỷ lệ thắng chung (%)')
    
    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'betting_statistics'
        ordering = ['-period_start', '-period']
        unique_together = ('period', 'period_start')
        indexes = [
            models.Index(fields=['period', 'period_start']),
            models.Index(fields=['total_bets_placed']),
            models.Index(fields=['total_stake_amount']),
        ]
        verbose_name = 'Betting Statistics'
        verbose_name_plural = 'Betting Statistics'
    
    def __str__(self):
        return f"{self.get_period_display()} - {self.period_start.date()} ({self.total_bets_placed} bets)"
    
    def calculate_house_edge(self):
        """Tính biên lợi nhuận của nhà cái"""
        if self.total_stake_amount > 0:
            return ((self.total_stake_amount - self.total_return_amount) / self.total_stake_amount) * 100
        return 0
    
    def calculate_win_rate(self):
        """Tính tỷ lệ thắng chung"""
        if self.total_bets_placed > 0:
            # Giả sử tỷ lệ thắng dựa trên số tiền trả về so với số tiền cược
            return (self.total_return_amount / self.total_stake_amount) * 100
        return 0
    
    def calculate_average_bet_size(self):
        """Tính số tiền cược trung bình"""
        if self.total_bets_placed > 0:
            return self.total_stake_amount / self.total_bets_placed
        return 0
    
    def save(self, *args, **kwargs):
        """Tự động tính toán các giá trị trước khi lưu"""
        self.house_edge = self.calculate_house_edge()
        self.win_rate = self.calculate_win_rate()
        self.average_bet_size = self.calculate_average_bet_size()
        super().save(*args, **kwargs)


class PerformanceMetrics(models.Model):
    """Metrics về hiệu suất người chơi theo từng môn thể thao và loại cược"""
    
    # Thông tin cơ bản
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                            related_name='performance_metrics')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, null=True, blank=True,
                             help_text='Môn thể thao (null = tất cả)')
    bet_type = models.ForeignKey(BetType, on_delete=models.CASCADE, null=True, blank=True,
                                help_text='Loại cược (null = tất cả)')
    
    # Thống kê cơ bản
    total_bets = models.IntegerField(default=0, help_text='Tổng số phiếu cược')
    total_wins = models.IntegerField(default=0, help_text='Tổng số phiếu thắng')
    total_losses = models.IntegerField(default=0, help_text='Tổng số phiếu thua')
    
    # Tỷ lệ và hiệu suất
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                     help_text='Tỷ lệ thành công (%)')
    win_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                 help_text='Tỷ lệ thắng (%)')
    
    # Thống kê tài chính
    total_stake = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                    help_text='Tổng số tiền cược')
    total_return = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                     help_text='Tổng số tiền nhận về')
    profit_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0,
                                    help_text='Lãi/lỗ')
    roi = models.DecimalField(max_digits=8, decimal_places=4, default=0,
                             help_text='Return on Investment (%)')
    
    # Thống kê odds
    average_odds = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                     help_text='Tỷ lệ cược trung bình')
    best_odds = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                  help_text='Tỷ lệ cược tốt nhất')
    worst_odds = models.DecimalField(max_digits=5, decimal_places=2, default=0,
                                   help_text='Tỷ lệ cược tệ nhất')
    
    # Thống kê theo thời gian
    first_bet_date = models.DateTimeField(null=True, blank=True, 
                                        help_text='Ngày đặt cược đầu tiên')
    last_bet_date = models.DateTimeField(null=True, blank=True,
                                       help_text='Ngày đặt cược cuối cùng')
    
    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'performance_metrics'
        ordering = ['-success_rate', '-roi']
        unique_together = ('user', 'sport', 'bet_type')
        indexes = [
            models.Index(fields=['user', 'sport']),
            models.Index(fields=['user', 'bet_type']),
            models.Index(fields=['success_rate']),
            models.Index(fields=['roi']),
        ]
        verbose_name = 'Performance Metric'
        verbose_name_plural = 'Performance Metrics'
    
    def __str__(self):
        sport_name = self.sport.name if self.sport else 'All Sports'
        bet_type_name = self.bet_type.name if self.bet_type else 'All Types'
        return f"{self.user.email} - {sport_name} - {bet_type_name}"
    
    def calculate_success_rate(self):
        """Tính tỷ lệ thành công"""
        if self.total_bets > 0:
            return (self.total_wins / self.total_bets) * 100
        return 0
    
    def calculate_win_rate(self):
        """Tính tỷ lệ thắng"""
        if self.total_bets > 0:
            return (self.total_wins / self.total_bets) * 100
        return 0
    
    def calculate_roi(self):
        """Tính Return on Investment"""
        if self.total_stake > 0:
            return ((self.total_return - self.total_stake) / self.total_stake) * 100
        return 0
    
    def save(self, *args, **kwargs):
        """Tự động tính toán các giá trị trước khi lưu"""
        self.success_rate = self.calculate_success_rate()
        self.win_rate = self.calculate_win_rate()
        self.roi = self.calculate_roi()
        super().save(*args, **kwargs)


class CashOutHistory(models.Model):
    """Lịch sử các giao dịch Cash Out"""
    
    CASHOUT_STATUS_CHOICES = [
        ('REQUESTED', 'Requested (Đã yêu cầu)'),
        ('PROCESSING', 'Processing (Đang xử lý)'),
        ('COMPLETED', 'Completed (Hoàn thành)'),
        ('FAILED', 'Failed (Thất bại)'),
        ('CANCELLED', 'Cancelled (Đã hủy)'),
    ]
    
    # Thông tin phiếu cược
    bet_slip = models.ForeignKey(BetSlip, on_delete=models.CASCADE, related_name='cashout_history')
    
    # Thông tin Cash Out
    requested_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                         help_text='Số tiền Cash Out được yêu cầu')
    fair_value = models.DecimalField(max_digits=10, decimal_places=2,
                                   help_text='Giá trị công bằng trước khi trừ phí')
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                   help_text='Số tiền phí Cash Out')
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=4,
                                       help_text='Tỷ lệ phí Cash Out')
    final_amount = models.DecimalField(max_digits=10, decimal_places=2,
                                     help_text='Số tiền cuối cùng người chơi nhận được')
    
    # Trạng thái và thời gian
    status = models.CharField(max_length=20, choices=CASHOUT_STATUS_CHOICES, default='REQUESTED')
    requested_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Thông tin odds
    original_odds = models.DecimalField(max_digits=5, decimal_places=2,
                                      help_text='Tỷ lệ cược gốc tại thời điểm đặt cược')
    live_odds = models.DecimalField(max_digits=5, decimal_places=2,
                                  help_text='Tỷ lệ cược trực tiếp tại thời điểm Cash Out')
    
    # Thông tin giao dịch
    saga_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    wallet_transaction_id = models.CharField(max_length=255, blank=True, null=True)
    
    # Thông tin người dùng
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                            related_name='cashout_transactions')
    
    # Lý do thất bại (nếu có)
    failure_reason = models.TextField(blank=True, null=True)
    
    # Metadata
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['bet_slip']),
            models.Index(fields=['requested_at']),
            models.Index(fields=['saga_transaction_id']),
        ]
        verbose_name = 'Cash Out History'
        verbose_name_plural = 'Cash Out Histories'
    
    def __str__(self):
        return f"Cash Out #{self.id} for BetSlip #{self.bet_slip.id} - {self.get_status_display()}"
    
    @property
    def profit_loss(self):
        """Tính lãi/lỗ từ Cash Out"""
        return self.final_amount - self.bet_slip.total_stake
    
    @property
    def processing_time(self):
        """Thời gian xử lý Cash Out"""
        if self.processed_at and self.requested_at:
            return self.processed_at - self.requested_at
        return None
    
    def mark_processing(self):
        """Đánh dấu đang xử lý"""
        self.status = 'PROCESSING'
        self.processed_at = timezone.now()
        self.save()
    
    def mark_completed(self, wallet_transaction_id=None):
        """Đánh dấu hoàn thành"""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        if wallet_transaction_id:
            self.wallet_transaction_id = wallet_transaction_id
        self.save()
    
    def mark_failed(self, reason=""):
        """Đánh dấu thất bại"""
        self.status = 'FAILED'
        self.failure_reason = reason
        self.save()
    
    def mark_cancelled(self, reason=""):
        """Đánh dấu đã hủy"""
        self.status = 'CANCELLED'
        self.failure_reason = reason
        self.save()


class BetSlipOwnership(models.Model):
    """Quản lý quyền sở hữu phân mảnh của phiếu cược"""
    
    bet_slip = models.ForeignKey(BetSlip, on_delete=models.CASCADE, related_name="ownerships")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bet_slip_ownerships")
    ownership_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Tỷ lệ sở hữu (ví dụ: 100.0, 90.0, 10.0)"
    )
    acquired_at = models.DateTimeField(auto_now_add=True)
    acquired_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Giá mua phần sở hữu này"
    )
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('bet_slip', 'owner')
        indexes = [
            models.Index(fields=['bet_slip', 'owner']),
            models.Index(fields=['ownership_percentage']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.owner.username} owns {self.ownership_percentage}% of BetSlip #{self.bet_slip.id}"
    
    @property
    def ownership_value(self):
        """Giá trị sở hữu dựa trên tỷ lệ"""
        return (self.bet_slip.total_stake * self.ownership_percentage) / 100
    
    @property
    def potential_payout(self):
        """Tiền thắng tiềm năng dựa trên tỷ lệ sở hữu"""
        if self.bet_slip.status == 'ACTIVE':
            return (self.bet_slip.potential_payout * self.ownership_percentage) / 100
        return Decimal('0.00')


class OrderBook(models.Model):
    """Sổ lệnh mua/bán phiếu cược trên P2P Marketplace"""
    
    ORDER_TYPE_CHOICES = [
        ('BUY', 'Buy Order (Lệnh mua)'),
        ('SELL', 'Sell Order (Lệnh bán)'),
    ]
    
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending (Chờ khớp)'),
        ('PARTIAL_FILL', 'Partial Fill (Khớp một phần)'),
        ('FILLED', 'Filled (Đã khớp hoàn toàn)'),
        ('CANCELLED', 'Cancelled (Đã hủy)'),
        ('EXPIRED', 'Expired (Hết hạn)'),
    ]
    
    # Thông tin lệnh
    order_type = models.CharField(max_length=10, choices=ORDER_TYPE_CHOICES)
    bet_slip = models.ForeignKey(BetSlip, on_delete=models.CASCADE, related_name="orders")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="placed_orders")
    
    # Thông tin giá và số lượng
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Giá mua/bán mỗi phần")
    quantity = models.IntegerField(help_text="Số phần sở hữu muốn mua/bán")
    filled_quantity = models.IntegerField(default=0, help_text="Số phần đã được khớp")
    
    # Trạng thái lệnh
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
    
    # Thời gian
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(help_text="Thời gian hết hạn lệnh")
    
    # Tùy chọn
    allow_partial_fill = models.BooleanField(default=True, help_text="Cho phép khớp một phần")
    is_fractional = models.BooleanField(default=False, help_text="Lệnh phân mảnh")
    
    class Meta:
        indexes = [
            models.Index(fields=['bet_slip', 'order_type', 'status']),
            models.Index(fields=['price', 'created_at']),
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['user', 'status']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_order_type_display()} - {self.quantity} parts at {self.price} by {self.user.username}"
    
    @property
    def remaining_quantity(self):
        """Số phần còn lại chưa khớp"""
        return self.quantity - self.filled_quantity
    
    @property
    def total_value(self):
        """Tổng giá trị lệnh"""
        return self.price * self.quantity
    
    @property
    def is_expired(self):
        """Kiểm tra lệnh có hết hạn chưa"""
        return timezone.now() > self.expires_at
    
    def can_fill(self, fill_quantity):
        """Kiểm tra có thể khớp số lượng này không"""
        if self.status != 'PENDING':
            return False
        if self.is_expired:
            return False
        if fill_quantity > self.remaining_quantity:
            return False
        return True
    
    def fill_order(self, fill_quantity):
        """Khớp lệnh với số lượng cụ thể"""
        if not self.can_fill(fill_quantity):
            return False
        
        self.filled_quantity += fill_quantity
        
        if self.filled_quantity >= self.quantity:
            self.status = 'FILLED'
        elif self.filled_quantity > 0:
            self.status = 'PARTIAL_FILL'
        
        self.save()
        return True


class MarketSuspension(models.Model):
    """Quản lý việc tạm khóa thị trường P2P khi có sự kiện quan trọng"""
    
    SUSPENSION_TYPE_CHOICES = [
        ('GOAL', 'Goal Scored (Bàn thắng)'),
        ('RED_CARD', 'Red Card (Thẻ đỏ)'),
        ('PENALTY', 'Penalty (Phạt đền)'),
        ('INJURY', 'Injury (Chấn thương)'),
        ('WEATHER', 'Weather (Thời tiết)'),
        ('MANUAL', 'Manual Suspension (Tạm khóa thủ công)'),
        ('API_EVENT', 'API Event (Sự kiện từ API)'),
    ]
    
    SUSPENSION_STATUS_CHOICES = [
        ('ACTIVE', 'Active (Đang tạm khóa)'),
        ('RESUMED', 'Resumed (Đã mở lại)'),
        ('EXPIRED', 'Expired (Hết hạn)'),
    ]
    
    # Thông tin tạm khóa
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="market_suspensions")
    suspension_type = models.CharField(max_length=20, choices=SUSPENSION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=SUSPENSION_STATUS_CHOICES, default='ACTIVE')
    
    # Thời gian
    suspended_at = models.DateTimeField(auto_now_add=True)
    resumed_at = models.DateTimeField(null=True, blank=True)
    duration_minutes = models.IntegerField(default=5, help_text="Thời gian tạm khóa (phút)")
    
    # Phạm vi tạm khóa
    p2p_orders_suspended = models.BooleanField(default=True, help_text="Tạm khóa lệnh P2P")
    new_bets_suspended = models.BooleanField(default=False, help_text="Tạm khóa đặt cược mới")
    cash_out_suspended = models.BooleanField(default=False, help_text="Tạm khóa Cash Out")
    
    # Thông tin bổ sung
    reason = models.TextField(blank=True, help_text="Lý do tạm khóa")
    api_event_data = models.JSONField(default=dict, blank=True, help_text="Dữ liệu sự kiện từ API")
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_suspensions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['match', 'status']),
            models.Index(fields=['suspension_type', 'status']),
            models.Index(fields=['suspended_at', 'resumed_at']),
            models.Index(fields=['status', 'created_at']),
        ]
        ordering = ['-suspended_at']
    
    def __str__(self):
        return f"Market Suspension for {self.match} - {self.get_suspension_type_display()}"
    
    @property
    def is_active(self):
        """Kiểm tra thị trường có đang bị tạm khóa không"""
        return self.status == 'ACTIVE'
    
    @property
    def suspension_duration(self):
        """Thời gian đã tạm khóa"""
        if self.resumed_at:
            return self.resumed_at - self.suspended_at
        return timezone.now() - self.suspended_at
    
    def resume_market(self, resumed_by=None):
        """Mở lại thị trường"""
        if self.status != 'ACTIVE':
            return False
        
        self.status = 'RESUMED'
        self.resumed_at = timezone.now()
        if resumed_by:
            self.created_by = resumed_by
        self.save()
        return True
    
    def auto_resume(self):
        """Tự động mở lại thị trường sau thời gian quy định"""
        if self.status != 'ACTIVE':
            return False
        
        if timezone.now() >= (self.suspended_at + timezone.timedelta(minutes=self.duration_minutes)):
            self.status = 'RESUMED'
            self.resumed_at = timezone.now()
            self.save()
            return True
        return False


class TradingSession(models.Model):
    """Quản lý phiên giao dịch P2P theo session để đảm bảo công bằng"""
    
    SESSION_TYPE_CHOICES = [
        ('COLLECTION', 'Order Collection (Thu thập lệnh)'),
        ('MATCHING', 'Order Matching (Khớp lệnh)'),
        ('CLOSED', 'Session Closed (Phiên kết thúc)'),
    ]
    
    SESSION_STATUS_CHOICES = [
        ('PREPARING', 'Preparing (Chuẩn bị)'),
        ('COLLECTING', 'Collecting (Đang thu thập)'),
        ('MATCHING', 'Matching (Đang khớp lệnh)'),
        ('CLOSED', 'Closed (Đã kết thúc)'),
        ('CANCELLED', 'Cancelled (Đã hủy)'),
    ]
    
    # Thông tin phiên
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="trading_sessions")
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='PREPARING')
    
    # Thời gian phiên
    start_time = models.DateTimeField(help_text="Thời gian bắt đầu phiên")
    end_time = models.DateTimeField(help_text="Thời gian kết thúc phiên")
    collection_duration = models.IntegerField(default=30, help_text="Thời gian thu thập lệnh (giây)")
    matching_duration = models.IntegerField(default=10, help_text="Thời gian khớp lệnh (giây)")
    
    # Quản lý lệnh
    orders_collected = models.ManyToManyField(OrderBook, blank=True, related_name="trading_sessions")
    total_orders = models.IntegerField(default=0, help_text="Tổng số lệnh được thu thập")
    matched_orders = models.IntegerField(default=0, help_text="Số lệnh đã khớp")
    
    # Kết quả phiên
    session_results = models.JSONField(default=dict, blank=True, help_text="Kết quả chi tiết của phiên")
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='created_trading_sessions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['match', 'status']),
            models.Index(fields=['session_type', 'status']),
            models.Index(fields=['start_time', 'end_time']),
            models.Index(fields=['status', 'created_at']),
        ]
        ordering = ['-start_time']
    
    def __str__(self):
        return f"Trading Session for {self.match} - {self.get_session_type_display()}"
    
    @property
    def is_active(self):
        """Kiểm tra phiên có đang hoạt động không"""
        now = timezone.now()
        return self.start_time <= now <= self.end_time
    
    @property
    def is_collecting(self):
        """Kiểm tra có đang trong giai đoạn thu thập lệnh không"""
        return self.status == 'COLLECTING'
    
    @property
    def is_matching(self):
        """Kiểm tra có đang trong giai đoạn khớp lệnh không"""
        return self.status == 'MATCHING'
    
    @property
    def time_remaining(self):
        """Thời gian còn lại của phiên"""
        now = timezone.now()
        if now > self.end_time:
            return timezone.timedelta(0)
        return self.end_time - now
    
    def start_collection_phase(self):
        """Bắt đầu giai đoạn thu thập lệnh"""
        if self.status != 'PREPARING':
            return False
        
        self.status = 'COLLECTING'
        self.start_time = timezone.now()
        self.end_time = self.start_time + timezone.timedelta(seconds=self.collection_duration)
        self.save()
        return True
    
    def start_matching_phase(self):
        """Bắt đầu giai đoạn khớp lệnh"""
        if self.status != 'COLLECTING':
            return False
        
        self.status = 'MATCHING'
        self.total_orders = self.orders_collected.count()
        self.save()
        return True
    
    def close_session(self):
        """Kết thúc phiên giao dịch"""
        if self.status not in ['COLLECTING', 'MATCHING']:
            return False
        
        self.status = 'CLOSED'
        self.end_time = timezone.now()
        self.save()
        return True
    
    def add_order(self, order):
        """Thêm lệnh vào phiên giao dịch"""
        if self.status != 'COLLECTING':
            return False
        
        self.orders_collected.add(order)
        return True


class P2PTransaction(models.Model):
    """Quản lý các giao dịch P2P mua/bán phiếu cược"""
    
    TRANSACTION_STATUS_CHOICES = [
        ('PENDING', 'Pending (Chờ xử lý)'),
        ('PROCESSING', 'Processing (Đang xử lý)'),
        ('COMPLETED', 'Completed (Hoàn thành)'),
        ('FAILED', 'Failed (Thất bại)'),
        ('CANCELLED', 'Cancelled (Đã hủy)'),
        ('REFUNDED', 'Refunded (Đã hoàn tiền)'),
    ]
    
    TRANSACTION_TYPE_CHOICES = [
        ('BUY', 'Buy (Mua)'),
        ('SELL', 'Sell (Bán)'),
        ('FRACTIONAL_BUY', 'Fractional Buy (Mua từng phần)'),
        ('FRACTIONAL_SELL', 'Fractional Sell (Bán từng phần)'),
    ]
    
    # Thông tin giao dịch
    transaction_id = models.CharField(max_length=50, unique=True, help_text="ID giao dịch duy nhất")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='PENDING')
    
    # Các bên tham gia
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='p2p_buys'
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='p2p_sells'
    )
    
    # Thông tin phiếu cược
    bet_slip = models.ForeignKey(BetSlip, on_delete=models.CASCADE, related_name="p2p_transactions")
    quantity = models.IntegerField(help_text="Số phần sở hữu được giao dịch")
    ownership_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Tỷ lệ sở hữu được giao dịch"
    )
    
    # Thông tin tài chính
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, help_text="Giá mỗi phần")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Tổng số tiền giao dịch")
    transaction_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, help_text="Phí giao dịch")
    net_amount_seller = models.DecimalField(max_digits=10, decimal_places=2, help_text="Số tiền người bán nhận được")
    
    # Thông tin lệnh
    buy_order = models.ForeignKey(
        OrderBook, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='buy_transactions'
    )
    sell_order = models.ForeignKey(
        OrderBook, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='sell_transactions'
    )
    
    # Thời gian
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Thông tin bổ sung
    notes = models.TextField(blank=True, help_text="Ghi chú giao dịch")
    error_message = models.TextField(blank=True, help_text="Thông báo lỗi nếu có")
    
    class Meta:
        indexes = [
            models.Index(fields=['transaction_id']),
            models.Index(fields=['buyer', 'status']),
            models.Index(fields=['seller', 'status']),
            models.Index(fields=['bet_slip', 'status']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['transaction_type', 'status']),
        ]
        ordering = ['-created_at']
    
    def __str__(self):
        return f"P2P Transaction {self.transaction_id} - {self.get_transaction_type_display()}"
    
    def save(self, *args, **kwargs):
        # Tự động tạo transaction_id nếu chưa có
        if not self.transaction_id:
            self.transaction_id = f"P2P_{timezone.now().strftime('%Y%m%d_%H%M%S')}_{self.id or 'NEW'}"
        
        # Tự động tính toán các giá trị
        if self.price_per_unit and self.quantity:
            self.total_amount = self.price_per_unit * self.quantity
            self.net_amount_seller = self.total_amount - self.transaction_fee
        
        super().save(*args, **kwargs)
    
    @property
    def is_completed(self):
        """Kiểm tra giao dịch đã hoàn thành chưa"""
        return self.status == 'COMPLETED'
    
    @property
    def is_failed(self):
        """Kiểm tra giao dịch có thất bại không"""
        return self.status in ['FAILED', 'CANCELLED', 'REFUNDED']
    
    @property
    def processing_time(self):
        """Thời gian xử lý giao dịch"""
        if self.completed_at and self.created_at:
            return self.completed_at - self.created_at
        return None
    
    def process_transaction(self):
        """Xử lý giao dịch"""
        if self.status != 'PENDING':
            return False
        
        self.status = 'PROCESSING'
        self.processed_at = timezone.now()
        self.save()
        return True
    
    def complete_transaction(self):
        """Hoàn thành giao dịch"""
        if self.status != 'PROCESSING':
            return False
        
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        self.save()
        
        # Tích hợp với User Rating Service
        try:
            from django.core.cache import cache
            import requests
            import json
            
            # Gửi webhook để cập nhật trade stats
            self._update_user_rating_after_completion()
            
        except Exception as e:
            # Log lỗi nhưng không làm fail giao dịch
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating user rating after P2P completion: {e}")
        
        return True
    
    def _update_user_rating_after_completion(self):
        """Cập nhật user rating sau khi giao dịch hoàn thành"""
        try:
            import requests
            import json
            
            # Cập nhật trade stats cho buyer
            buyer_data = {
                'user_id': str(self.buyer.id),
                'trade_success': True
            }
            
            seller_data = {
                'user_id': str(self.seller.id),
                'trade_success': True
            }
            
            # Gọi User Rating Service để cập nhật trade stats
            rating_service_url = "http://user_rating_service:8000/api/trust-scores/update_trade_stats/"
            
            # Cập nhật cho buyer
            requests.post(
                rating_service_url,
                json=buyer_data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            # Cập nhật cho seller
            requests.post(
                rating_service_url,
                json=seller_data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            # Kiểm tra và trao badge tự động
            self._check_and_award_badges()
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in _update_user_rating_after_completion: {e}")
    
    def _check_and_award_badges(self):
        """Kiểm tra và trao badge tự động"""
        try:
            import requests
            
            # Kiểm tra badge cho buyer
            buyer_badge_url = "http://user_rating_service:8000/api/badges/award_badge/"
            buyer_badge_data = {'user_id': str(self.buyer.id)}
            
            requests.post(
                buyer_badge_url,
                json=buyer_badge_data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
            # Kiểm tra badge cho seller
            seller_badge_data = {'user_id': str(self.seller.id)}
            
            requests.post(
                buyer_badge_url,
                json=seller_badge_data,
                headers={'Content-Type': 'application/json'},
                timeout=5
            )
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error in _check_and_award_badges: {e}")
    
    def fail_transaction(self, error_message=""):
        """Đánh dấu giao dịch thất bại"""
        if self.status not in ['PENDING', 'PROCESSING']:
            return False
        
        self.status = 'FAILED'
        self.error_message = error_message
        self.save()
        return True
    
    def cancel_transaction(self):
        """Hủy giao dịch"""
        if self.status not in ['PENDING', 'PROCESSING']:
            return False
        
        self.status = 'CANCELLED'
        self.save()
        return True


