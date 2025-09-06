from django.db import models
from django.utils import timezone
import uuid

class SagaTransaction(models.Model):
    """Main saga transaction model"""
    
    SAGA_TYPES = [
        ('betting_flow', 'Betting Flow'),
        ('deposit_flow', 'Deposit Flow'),
        ('withdrawal_flow', 'Withdrawal Flow'),
        ('refund_flow', 'Refund Flow'),
        ('promotion_flow', 'Promotion Flow'),
        # ============================================================================
        # NEW SAGA TYPES FOR CASH OUT SUPPORT
        # ============================================================================
        ('cashout_flow', 'Cash Out Flow'),
        ('cashout_rollback_flow', 'Cash Out Rollback Flow'),
        ('cashout_compensation_flow', 'Cash Out Compensation Flow'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('compensating', 'Compensating'),
        ('compensated', 'Compensated'),
        ('timeout', 'Timeout'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    saga_type = models.CharField(max_length=50, choices=SAGA_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    user_id = models.IntegerField()
    correlation_id = models.CharField(max_length=255, unique=True)
    
    # Saga data and context
    input_data = models.JSONField(default=dict)
    context_data = models.JSONField(default=dict)
    result_data = models.JSONField(default=dict)
    
    # Timing
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    timeout_at = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    class Meta:
        db_table = 'saga_transactions'
        indexes = [
            models.Index(fields=['saga_type']),
            models.Index(fields=['status']),
            models.Index(fields=['user_id']),
            models.Index(fields=['correlation_id']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Saga {self.saga_type} - {self.status} - {self.correlation_id}"

class SagaStep(models.Model):
    """Individual step in a saga transaction"""
    
    STEP_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('compensating', 'Compensating'),
        ('compensated', 'Compensated'),
        ('skipped', 'Skipped'),
    ]
    
    STEP_TYPES = [
        ('service_call', 'Service Call'),
        ('compensation', 'Compensation'),
        ('validation', 'Validation'),
        ('notification', 'Notification'),
        # ============================================================================
        # NEW STEP TYPES FOR CASH OUT SUPPORT
        # ============================================================================
        ('risk_management_call', 'Risk Management Service Call'),
        ('wallet_operation', 'Wallet Operation'),
        ('betting_service_call', 'Betting Service Call'),
        ('cashout_validation', 'Cash Out Validation'),
        ('liability_update', 'Liability Update'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    saga_transaction = models.ForeignKey(SagaTransaction, on_delete=models.CASCADE, related_name='steps')
    
    step_name = models.CharField(max_length=100)
    step_type = models.CharField(max_length=20, choices=STEP_TYPES, default='service_call')
    step_order = models.IntegerField()
    status = models.CharField(max_length=20, choices=STEP_STATUS_CHOICES, default='pending')
    
    # Service information
    service_name = models.CharField(max_length=50)
    service_endpoint = models.CharField(max_length=255)
    http_method = models.CharField(max_length=10, default='POST')
    
    # Request/Response data
    request_data = models.JSONField(default=dict)
    response_data = models.JSONField(default=dict)
    headers = models.JSONField(default=dict)
    
    # Compensation information
    compensation_service = models.CharField(max_length=50, blank=True, null=True)
    compensation_endpoint = models.CharField(max_length=255, blank=True, null=True)
    compensation_method = models.CharField(max_length=10, default='POST')
    compensation_data = models.JSONField(default=dict)
    
    # Timing
    created_at = models.DateTimeField(default=timezone.now)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True, null=True)
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    
    class Meta:
        db_table = 'saga_steps'
        unique_together = ['saga_transaction', 'step_order']
        indexes = [
            models.Index(fields=['saga_transaction', 'step_order']),
            models.Index(fields=['status']),
            models.Index(fields=['service_name']),
        ]
    
    def __str__(self):
        return f"Step {self.step_order}: {self.step_name} - {self.status}"

class SagaEvent(models.Model):
    """Events and logs for saga transactions"""
    
    EVENT_TYPES = [
        ('saga_started', 'Saga Started'),
        ('saga_completed', 'Saga Completed'),
        ('saga_failed', 'Saga Failed'),
        ('saga_timeout', 'Saga Timeout'),
        ('step_started', 'Step Started'),
        ('step_completed', 'Step Completed'),
        ('step_failed', 'Step Failed'),
        ('compensation_started', 'Compensation Started'),
        ('compensation_completed', 'Compensation Completed'),
        ('compensation_failed', 'Compensation Failed'),
        ('retry_attempted', 'Retry Attempted'),
        # ============================================================================
        # NEW EVENT TYPES FOR CASH OUT SUPPORT
        # ============================================================================
        ('cashout_requested', 'Cash Out Requested'),
        ('cashout_funds_credited', 'Cash Out Funds Credited'),
        ('cashout_failed', 'Cash Out Failed'),
        ('cashout_completed', 'Cash Out Completed'),
        ('cashout_liability_updated', 'Cash Out Liability Updated'),
        ('cashout_rollback_initiated', 'Cash Out Rollback Initiated'),
        ('cashout_rollback_completed', 'Cash Out Rollback Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    saga_transaction = models.ForeignKey(SagaTransaction, on_delete=models.CASCADE, related_name='events')
    saga_step = models.ForeignKey(SagaStep, on_delete=models.CASCADE, null=True, blank=True, related_name='events')
    
    event_type = models.CharField(max_length=30, choices=EVENT_TYPES)
    event_data = models.JSONField(default=dict)
    message = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        db_table = 'saga_events'
        indexes = [
            models.Index(fields=['saga_transaction', 'created_at']),
            models.Index(fields=['event_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.created_at}"

class SagaDefinition(models.Model):
    """Saga workflow definitions"""
    
    name = models.CharField(max_length=100, unique=True)
    saga_type = models.CharField(max_length=50, choices=SagaTransaction.SAGA_TYPES)
    description = models.TextField(blank=True, null=True)
    
    # Workflow definition as JSON
    workflow_definition = models.JSONField(default=dict)
    
    # Configuration
    timeout_seconds = models.IntegerField(default=300)
    max_retries = models.IntegerField(default=3)
    retry_delay_seconds = models.IntegerField(default=5)
    
    is_active = models.BooleanField(default=True)
    version = models.CharField(max_length=20, default='1.0')
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'saga_definitions'
        unique_together = ['name', 'version']
    
    def __str__(self):
        return f"{self.name} v{self.version}"

# ============================================================================
# NEW MODELS FOR CASH OUT SAGA SUPPORT
# ============================================================================

class CashOutSagaDefinition(models.Model):
    """Chuyên biệt cho Cash Out Saga workflow"""
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    # Cash Out specific configuration
    allow_partial_cashout = models.BooleanField(default=False, help_text='Cho phép Cash Out một phần')
    require_confirmation = models.BooleanField(default=True, help_text='Yêu cầu xác nhận từ người dùng')
    auto_rollback_on_failure = models.BooleanField(default=True, help_text='Tự động rollback khi thất bại')
    
    # Workflow steps definition
    workflow_steps = models.JSONField(default=list, help_text='Định nghĩa các bước trong workflow')
    
    # Timeout và retry configuration
    quote_expiry_seconds = models.IntegerField(default=10, help_text='Thời gian hết hạn báo giá (giây)')
    processing_timeout_seconds = models.IntegerField(default=60, help_text='Timeout xử lý Cash Out (giây)')
    max_retries = models.IntegerField(default=3, help_text='Số lần retry tối đa')
    retry_delay_seconds = models.IntegerField(default=5, help_text='Delay giữa các lần retry (giây)')
    
    # Risk management configuration
    require_live_odds_validation = models.BooleanField(default=True, help_text='Yêu cầu validate live odds')
    min_confidence_score = models.DecimalField(max_digits=3, decimal_places=2, default=0.8, help_text='Độ tin cậy tối thiểu của live odds')
    
    # Status
    is_active = models.BooleanField(default=True)
    version = models.CharField(max_length=20, default='1.0')
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cashout_saga_definitions'
        unique_together = ['name', 'version']
        verbose_name = 'Cash Out Saga Definition'
        verbose_name_plural = 'Cash Out Saga Definitions'
    
    def __str__(self):
        return f"Cash Out Saga: {self.name} v{self.version}"
    
    def get_default_workflow_steps(self):
        """Trả về workflow steps mặc định cho Cash Out"""
        return [
            {
                'step_order': 1,
                'step_name': 'Validate Cash Out Eligibility',
                'step_type': 'cashout_validation',
                'service_name': 'betting_service',
                'service_endpoint': '/api/cashout/check-eligibility/',
                'http_method': 'GET',
                'compensation_service': None,
                'compensation_endpoint': None,
                'timeout_seconds': 10
            },
            {
                'step_order': 2,
                'step_name': 'Get Live Odds and Event Margin',
                'step_type': 'risk_management_call',
                'service_name': 'risk_management_service',
                'service_endpoint': '/api/cashout/live-odds/',
                'http_method': 'POST',
                'compensation_service': None,
                'compensation_endpoint': None,
                'timeout_seconds': 15
            },
            {
                'step_order': 3,
                'step_name': 'Calculate Cash Out Value',
                'step_type': 'betting_service_call',
                'service_name': 'betting_service',
                'service_endpoint': '/api/cashout/request-quote/',
                'http_method': 'POST',
                'compensation_service': None,
                'compensation_endpoint': None,
                'timeout_seconds': 10
            },
            {
                'step_order': 4,
                'step_name': 'Credit Funds to Wallet',
                'step_type': 'wallet_operation',
                'service_name': 'wallet_service',
                'service_endpoint': '/api/cashout/process/',
                'http_method': 'POST',
                'compensation_service': 'wallet_service',
                'compensation_endpoint': '/api/cashout/rollback/',
                'compensation_method': 'POST',
                'timeout_seconds': 30
            },
            {
                'step_order': 5,
                'step_name': 'Update Bet Slip Status',
                'step_type': 'betting_service_call',
                'service_name': 'betting_service',
                'service_endpoint': '/api/cashout/confirm/',
                'http_method': 'POST',
                'compensation_service': 'betting_service',
                'compensation_endpoint': '/api/cashout/cancel/',
                'compensation_method': 'POST',
                'timeout_seconds': 15
            },
            {
                'step_order': 6,
                'step_name': 'Update Liability and P&L',
                'step_type': 'liability_update',
                'service_name': 'risk_management_service',
                'service_endpoint': '/api/cashout/liability/update/',
                'http_method': 'POST',
                'compensation_service': 'risk_management_service',
                'compensation_endpoint': '/api/cashout/liability/rollback/',
                'compensation_method': 'POST',
                'timeout_seconds': 20
            }
        ]

class CashOutSagaInstance(models.Model):
    """Instance của một Cash Out Saga cụ thể"""
    
    STATUS_CHOICES = [
        ('initiated', 'Initiated (Đã khởi tạo)'),
        ('quote_requested', 'Quote Requested (Đã yêu cầu báo giá)'),
        ('quote_received', 'Quote Received (Đã nhận báo giá)'),
        ('user_confirmed', 'User Confirmed (Người dùng đã xác nhận)'),
        ('processing', 'Processing (Đang xử lý)'),
        ('completed', 'Completed (Hoàn thành)'),
        ('failed', 'Failed (Thất bại)'),
        ('rollback_initiated', 'Rollback Initiated (Đã bắt đầu rollback)'),
        ('rollback_completed', 'Rollback Completed (Rollback hoàn thành)'),
        ('cancelled', 'Cancelled (Đã hủy)'),
    ]
    
    # Core information
    saga_transaction = models.OneToOneField(SagaTransaction, on_delete=models.CASCADE, related_name='cashout_instance')
    bet_slip_id = models.CharField(max_length=255, help_text='ID của bet slip được Cash Out')
    user_id = models.CharField(max_length=255, help_text='ID của người dùng')
    
    # Cash Out details
    cashout_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    fair_value = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    fee_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    
    # Quote information
    quote_expiry_time = models.DateTimeField(null=True, blank=True)
    quote_is_valid = models.BooleanField(default=True)
    
    # Status tracking
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='initiated')
    current_step = models.IntegerField(default=1)
    total_steps = models.IntegerField(default=6)
    
    # Timestamps
    initiated_at = models.DateTimeField(auto_now_add=True)
    quote_requested_at = models.DateTimeField(null=True, blank=True)
    quote_received_at = models.DateTimeField(null=True, blank=True)
    user_confirmed_at = models.DateTimeField(null=True, blank=True)
    processing_started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    failed_at = models.DateTimeField(null=True, blank=True)
    
    # Error handling
    failure_reason = models.TextField(blank=True, null=True)
    last_error_step = models.IntegerField(null=True, blank=True)
    
    class Meta:
        db_table = 'cashout_saga_instances'
        indexes = [
            models.Index(fields=['bet_slip_id']),
            models.Index(fields=['user_id', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
        verbose_name = 'Cash Out Saga Instance'
        verbose_name_plural = 'Cash Out Saga Instances'
    
    def __str__(self):
        return f"Cash Out Saga #{self.id} for BetSlip #{self.bet_slip_id} - {self.get_status_display()}"
    
    @property
    def progress_percentage(self):
        """Tính phần trăm hoàn thành"""
        if self.status == 'completed':
            return 100
        elif self.status == 'failed':
            return 0
        else:
            return int((self.current_step / self.total_steps) * 100)
    
    @property
    def is_quote_expired(self):
        """Kiểm tra xem báo giá có hết hạn chưa"""
        if not self.quote_expiry_time:
            return False
        return timezone.now() > self.quote_expiry_time
    
    def mark_quote_requested(self):
        """Đánh dấu đã yêu cầu báo giá"""
        self.status = 'quote_requested'
        self.quote_requested_at = timezone.now()
        self.save()
    
    def mark_quote_received(self, cashout_data):
        """Đánh dấu đã nhận báo giá"""
        self.status = 'quote_received'
        self.quote_received_at = timezone.now()
        self.cashout_amount = cashout_data.get('cash_out_value')
        self.fair_value = cashout_data.get('fair_value')
        self.fee_amount = cashout_data.get('fee_amount')
        
        # Tính thời gian hết hạn (10 giây)
        from datetime import timedelta
        self.quote_expiry_time = timezone.now() + timedelta(seconds=10)
        
        self.save()
    
    def mark_user_confirmed(self):
        """Đánh dấu người dùng đã xác nhận"""
        self.status = 'user_confirmed'
        self.user_confirmed_at = timezone.now()
        self.save()
    
    def mark_processing(self):
        """Đánh dấu đang xử lý"""
        self.status = 'processing'
        self.processing_started_at = timezone.now()
        self.save()
    
    def mark_completed(self):
        """Đánh dấu hoàn thành"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.current_step = self.total_steps
        self.save()
    
    def mark_failed(self, reason="", step=None):
        """Đánh dấu thất bại"""
        self.status = 'failed'
        self.failed_at = timezone.now()
        self.failure_reason = reason
        if step:
            self.last_error_step = step
        self.save()
    
    def mark_rollback_initiated(self):
        """Đánh dấu đã bắt đầu rollback"""
        self.status = 'rollback_initiated'
        self.save()
    
    def mark_rollback_completed(self):
        """Đánh dấu rollback hoàn thành"""
        self.status = 'rollback_completed'
        self.save()
    
    def advance_step(self):
        """Tiến đến bước tiếp theo"""
        if self.current_step < self.total_steps:
            self.current_step += 1
            self.save()
    
    def can_proceed_to_next_step(self):
        """Kiểm tra xem có thể tiến đến bước tiếp theo không"""
        return self.status in ['initiated', 'quote_received', 'user_confirmed', 'processing']

