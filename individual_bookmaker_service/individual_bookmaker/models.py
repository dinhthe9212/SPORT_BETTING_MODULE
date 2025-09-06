from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid

class IndividualBookmaker(models.Model):
    """Model quản lý thông tin nhà cái cá nhân"""
    
    BOOKMAKER_STATUS_CHOICES = [
        ('ACTIVE', 'Active (Hoạt động)'),
        ('SUSPENDED', 'Suspended (Tạm dừng)'),
        ('INACTIVE', 'Inactive (Không hoạt động)'),
        ('PENDING_VERIFICATION', 'Pending Verification (Chờ xác minh)'),
    ]
    
    EXPERIENCE_LEVEL_CHOICES = [
        ('BEGINNER', 'Beginner (Mới bắt đầu)'),
        ('INTERMEDIATE', 'Intermediate (Trung bình)'),
        ('ADVANCED', 'Advanced (Nâng cao)'),
        ('EXPERT', 'Expert (Chuyên gia)'),
    ]
    
    # Thông tin cơ bản
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='individual_bookmaker')
    bookmaker_id = models.CharField(max_length=50, unique=True, default=uuid.uuid4)
    status = models.CharField(max_length=25, choices=BOOKMAKER_STATUS_CHOICES, default='PENDING_VERIFICATION')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default='BEGINNER')
    
    # Thông tin chuyên môn
    preferred_sports = models.JSONField(default=list, help_text='Danh sách môn thể thao ưa thích')
    max_bet_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, help_text='Số tiền cược tối đa cho phép')
    risk_tolerance = models.CharField(max_length=20, default='CONSERVATIVE', help_text='Mức độ chấp nhận rủi ro')
    
    # Thống kê hoạt động
    total_events_created = models.IntegerField(default=0, help_text='Tổng số sự kiện đã tạo')
    total_bets_placed = models.IntegerField(default=0, help_text='Tổng số cược đã đặt')
    total_profit_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text='Tổng lãi/lỗ')
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Tỷ lệ thành công (%)')
    
    # Cài đặt giáo dục
    education_enabled = models.BooleanField(default=True, help_text='Bật/tắt hệ thống giáo dục')
    auto_risk_alerts = models.BooleanField(default=True, help_text='Tự động gửi cảnh báo rủi ro')
    tutorial_reminders = models.BooleanField(default=True, help_text='Nhắc nhở học tutorial')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'individual_bookmakers'
        verbose_name = 'Individual Bookmaker'
        verbose_name_plural = 'Individual Bookmakers'
        indexes = [
            models.Index(fields=['status', 'experience_level']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['last_activity']),
        ]
    
    def __str__(self):
        return f"Bookmaker {self.user.username} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        # Cập nhật last_activity
        self.last_activity = timezone.now()
        super().save(*args, **kwargs)
    
    @property
    def is_active(self):
        return self.status == 'ACTIVE'
    
    @property
    def needs_education(self):
        """Kiểm tra xem có cần giáo dục thêm không"""
        return self.experience_level in ['BEGINNER', 'INTERMEDIATE'] and self.total_events_created < 10

class RiskEducationTutorial(models.Model):
    """Model quản lý các tutorial giáo dục về rủi ro"""
    
    TUTORIAL_CATEGORY_CHOICES = [
        ('RISK_MANAGEMENT', 'Risk Management (Quản lý rủi ro)'),
        ('BETTING_STRATEGY', 'Betting Strategy (Chiến lược cược)'),
        ('MONEY_MANAGEMENT', 'Money Management (Quản lý tiền)'),
        ('PSYCHOLOGY', 'Psychology (Tâm lý)'),
        ('TECHNICAL_ANALYSIS', 'Technical Analysis (Phân tích kỹ thuật)'),
        ('COMPLIANCE', 'Compliance (Tuân thủ)'),
    ]
    
    DIFFICULTY_LEVEL_CHOICES = [
        ('BEGINNER', 'Beginner (Mới bắt đầu)'),
        ('INTERMEDIATE', 'Intermediate (Trung bình)'),
        ('ADVANCED', 'Advanced (Nâng cao)'),
    ]
    
    # Thông tin cơ bản
    title = models.CharField(max_length=200, help_text='Tiêu đề tutorial')
    category = models.CharField(max_length=25, choices=TUTORIAL_CATEGORY_CHOICES)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVEL_CHOICES)
    description = models.TextField(help_text='Mô tả tutorial')
    content = models.TextField(help_text='Nội dung chi tiết')
    
    # Media và tài liệu
    video_url = models.URLField(blank=True, null=True, help_text='URL video tutorial')
    document_url = models.URLField(blank=True, null=True, help_text='URL tài liệu PDF')
    image_url = models.URLField(blank=True, null=True, help_text='URL hình ảnh minh họa')
    
    # Cài đặt tutorial
    estimated_duration = models.IntegerField(default=15, help_text='Thời gian ước tính (phút)')
    points_reward = models.IntegerField(default=10, help_text='Điểm thưởng khi hoàn thành')
    is_active = models.BooleanField(default=True, help_text='Tutorial có hoạt động không')
    requires_prerequisites = models.ManyToManyField('self', blank=True, symmetrical=False, help_text='Tutorial cần học trước')
    
    # Thống kê
    total_completions = models.IntegerField(default=0, help_text='Tổng số người hoàn thành')
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, help_text='Điểm đánh giá trung bình')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'risk_education_tutorials'
        ordering = ['difficulty_level', 'category', 'title']
        indexes = [
            models.Index(fields=['category', 'difficulty_level']),
            models.Index(fields=['is_active', 'difficulty_level']),
            models.Index(fields=['total_completions']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

class TutorialProgress(models.Model):
    """Model theo dõi tiến độ học tutorial của người dùng"""
    
    PROGRESS_STATUS_CHOICES = [
        ('NOT_STARTED', 'Not Started (Chưa bắt đầu)'),
        ('IN_PROGRESS', 'In Progress (Đang học)'),
        ('COMPLETED', 'Completed (Đã hoàn thành)'),
        ('FAILED', 'Failed (Thất bại)'),
    ]
    
    # Thông tin cơ bản
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tutorial_progress')
    tutorial = models.ForeignKey(RiskEducationTutorial, on_delete=models.CASCADE, related_name='user_progress')
    status = models.CharField(max_length=20, choices=PROGRESS_STATUS_CHOICES, default='NOT_STARTED')
    
    # Tiến độ học tập
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent = models.IntegerField(default=0, help_text='Thời gian học (giây)')
    progress_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Phần trăm hoàn thành')
    
    # Kết quả học tập
    quiz_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Điểm quiz')
    points_earned = models.IntegerField(default=0, help_text='Điểm đã kiếm được')
    attempts_count = models.IntegerField(default=0, help_text='Số lần thử')
    
    # Ghi chú và đánh giá
    notes = models.TextField(blank=True, help_text='Ghi chú cá nhân')
    rating = models.IntegerField(null=True, blank=True, help_text='Đánh giá (1-5)')
    feedback = models.TextField(blank=True, help_text='Phản hồi')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tutorial_progress'
        unique_together = ('user', 'tutorial')
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['tutorial', 'status']),
            models.Index(fields=['progress_percentage']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.tutorial.title} ({self.get_status_display()})"
    
    def start_tutorial(self):
        """Bắt đầu học tutorial"""
        if self.status == 'NOT_STARTED':
            self.status = 'IN_PROGRESS'
            self.started_at = timezone.now()
            self.save()
    
    def complete_tutorial(self, quiz_score=None, points_earned=None):
        """Hoàn thành tutorial"""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        if quiz_score is not None:
            self.quiz_score = quiz_score
        if points_earned is not None:
            self.points_earned = points_earned
        
        # Tính thời gian học
        if self.started_at:
            self.time_spent = int((self.completed_at - self.started_at).total_seconds())
        
        self.progress_percentage = 100.0
        self.save()

class RiskAlert(models.Model):
    """Model quản lý cảnh báo rủi ro cho nhà cái cá nhân"""
    
    ALERT_TYPE_CHOICES = [
        ('HIGH_RISK', 'High Risk (Rủi ro cao)'),
        ('MEDIUM_RISK', 'Medium Risk (Rủi ro trung bình)'),
        ('LOW_RISK', 'Low Risk (Rủi ro thấp)'),
        ('INFO', 'Information (Thông tin)'),
        ('WARNING', 'Warning (Cảnh báo)'),
        ('CRITICAL', 'Critical (Nguy hiểm)'),
    ]
    
    ALERT_STATUS_CHOICES = [
        ('ACTIVE', 'Active (Đang hoạt động)'),
        ('ACKNOWLEDGED', 'Acknowledged (Đã xác nhận)'),
        ('RESOLVED', 'Resolved (Đã giải quyết)'),
        ('EXPIRED', 'Expired (Hết hạn)'),
    ]
    
    ALERT_CATEGORY_CHOICES = [
        ('BETTING_LIMIT', 'Betting Limit (Giới hạn cược)'),
        ('LOSS_THRESHOLD', 'Loss Threshold (Ngưỡng thua lỗ)'),
        ('ODDS_MOVEMENT', 'Odds Movement (Biến động tỷ lệ)'),
        ('MARKET_VOLATILITY', 'Market Volatility (Biến động thị trường)'),
        ('COMPLIANCE_ISSUE', 'Compliance Issue (Vấn đề tuân thủ)'),
        ('TECHNICAL_ISSUE', 'Technical Issue (Vấn đề kỹ thuật)'),
        ('EDUCATION_REMINDER', 'Education Reminder (Nhắc nhở học tập)'),
    ]
    
    # Thông tin cơ bản
    bookmaker = models.ForeignKey(IndividualBookmaker, on_delete=models.CASCADE, related_name='risk_alerts')
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    category = models.CharField(max_length=25, choices=ALERT_CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=ALERT_STATUS_CHOICES, default='ACTIVE')
    
    # Nội dung cảnh báo
    title = models.CharField(max_length=200, help_text='Tiêu đề cảnh báo')
    message = models.TextField(help_text='Nội dung cảnh báo')
    description = models.TextField(blank=True, help_text='Mô tả chi tiết')
    
    # Dữ liệu rủi ro
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, help_text='Điểm rủi ro (0-100)')
    risk_data = models.JSONField(default=dict, help_text='Dữ liệu rủi ro chi tiết')
    recommended_actions = models.JSONField(default=list, help_text='Hành động khuyến nghị')
    
    # Cài đặt cảnh báo
    priority = models.IntegerField(default=1, help_text='Mức độ ưu tiên (1-5)')
    auto_resolve = models.BooleanField(default=False, help_text='Tự động giải quyết')
    expires_at = models.DateTimeField(null=True, blank=True, help_text='Thời gian hết hạn')
    
    # Thông tin xử lý
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='acknowledged_alerts')
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(blank=True, help_text='Ghi chú giải quyết')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_alerts')
    
    class Meta:
        db_table = 'risk_alerts'
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['bookmaker', 'status']),
            models.Index(fields=['alert_type', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['risk_score', 'status']),
            models.Index(fields=['expires_at', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.bookmaker.user.username} ({self.get_status_display()})"
    
    @property
    def is_expired(self):
        """Kiểm tra cảnh báo có hết hạn không"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def is_critical(self):
        """Kiểm tra có phải cảnh báo nguy hiểm không"""
        return self.alert_type == 'CRITICAL' or self.risk_score >= 80
    
    def acknowledge(self, user):
        """Xác nhận cảnh báo"""
        if self.status == 'ACTIVE':
            self.status = 'ACKNOWLEDGED'
            self.acknowledged_at = timezone.now()
            self.acknowledged_by = user
            self.save()
    
    def resolve(self, notes=""):
        """Giải quyết cảnh báo"""
        if self.status in ['ACTIVE', 'ACKNOWLEDGED']:
            self.status = 'RESOLVED'
            self.resolved_at = timezone.now()
            if notes:
                self.resolution_notes = notes
            self.save()

class BestPractice(models.Model):
    """Model quản lý các thực hành tốt nhất cho nhà cái cá nhân"""
    
    PRACTICE_CATEGORY_CHOICES = [
        ('RISK_MANAGEMENT', 'Risk Management (Quản lý rủi ro)'),
        ('BETTING_STRATEGY', 'Betting Strategy (Chiến lược cược)'),
        ('MONEY_MANAGEMENT', 'Money Management (Quản lý tiền)'),
        ('PSYCHOLOGY', 'Psychology (Tâm lý)'),
        ('TECHNICAL_ANALYSIS', 'Technical Analysis (Phân tích kỹ thuật)'),
        ('COMPLIANCE', 'Compliance (Tuân thủ)'),
        ('CUSTOMER_SERVICE', 'Customer Service (Dịch vụ khách hàng)'),
    ]
    
    # Thông tin cơ bản
    title = models.CharField(max_length=200, help_text='Tiêu đề thực hành tốt nhất')
    category = models.CharField(max_length=25, choices=PRACTICE_CATEGORY_CHOICES)
    description = models.TextField(help_text='Mô tả ngắn gọn')
    content = models.TextField(help_text='Nội dung chi tiết')
    
    # Hướng dẫn thực hiện
    steps = models.JSONField(default=list, help_text='Các bước thực hiện')
    examples = models.JSONField(default=list, help_text='Ví dụ minh họa')
    tips = models.JSONField(default=list, help_text='Mẹo và lưu ý')
    
    # Tài liệu tham khảo
    references = models.JSONField(default=list, help_text='Tài liệu tham khảo')
    external_links = models.JSONField(default=list, help_text='Liên kết ngoài')
    
    # Cài đặt
    difficulty_level = models.CharField(max_length=20, choices=IndividualBookmaker.EXPERIENCE_LEVEL_CHOICES)
    estimated_time = models.IntegerField(default=30, help_text='Thời gian ước tính thực hiện (phút)')
    is_active = models.BooleanField(default=True, help_text='Thực hành có hoạt động không')
    
    # Thống kê
    total_views = models.IntegerField(default=0, help_text='Tổng số lượt xem')
    total_implementations = models.IntegerField(default=0, help_text='Tổng số lần áp dụng')
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, help_text='Điểm đánh giá trung bình')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        db_table = 'best_practices'
        ordering = ['category', 'difficulty_level', 'title']
        indexes = [
            models.Index(fields=['category', 'difficulty_level']),
            models.Index(fields=['is_active', 'difficulty_level']),
            models.Index(fields=['total_views']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"

class BookmakerPerformance(models.Model):
    """Model theo dõi hiệu suất của nhà cái cá nhân"""
    
    PERIOD_CHOICES = [
        ('DAILY', 'Daily (Hàng ngày)'),
        ('WEEKLY', 'Weekly (Hàng tuần)'),
        ('MONTHLY', 'Monthly (Hàng tháng)'),
        ('QUARTERLY', 'Quarterly (Theo quý)'),
        ('YEARLY', 'Yearly (Hàng năm)'),
    ]
    
    # Thông tin cơ bản
    bookmaker = models.ForeignKey(IndividualBookmaker, on_delete=models.CASCADE, related_name='performance_records')
    period = models.CharField(max_length=20, choices=PERIOD_CHOICES)
    period_start = models.DateTimeField(help_text='Thời điểm bắt đầu kỳ')
    period_end = models.DateTimeField(help_text='Thời điểm kết thúc kỳ')
    
    # Thống kê hoạt động
    events_created = models.IntegerField(default=0, help_text='Số sự kiện đã tạo')
    bets_placed = models.IntegerField(default=0, help_text='Số cược đã đặt')
    bets_won = models.IntegerField(default=0, help_text='Số cược thắng')
    bets_lost = models.IntegerField(default=0, help_text='Số cược thua')
    
    # Thống kê tài chính
    total_stake = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text='Tổng số tiền cược')
    total_return = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text='Tổng số tiền nhận về')
    total_profit_loss = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text='Tổng lãi/lỗ')
    gross_margin = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Biên lợi nhuận gộp (%)')
    
    # Thống kê rủi ro
    max_drawdown = models.DecimalField(max_digits=15, decimal_places=2, default=0, help_text='Mức sụt giảm tối đa')
    risk_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Điểm rủi ro (0-100)')
    volatility = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Độ biến động (%)')
    
    # Thống kê giáo dục
    tutorials_completed = models.IntegerField(default=0, help_text='Số tutorial đã hoàn thành')
    education_score = models.DecimalField(max_digits=5, decimal_places=2, default=0, help_text='Điểm giáo dục')
    risk_alerts_count = models.IntegerField(default=0, help_text='Số cảnh báo rủi ro')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bookmaker_performance'
        unique_together = ('bookmaker', 'period', 'period_start')
        ordering = ['-period_start', '-period']
        indexes = [
            models.Index(fields=['bookmaker', 'period']),
            models.Index(fields=['period_start', 'period_end']),
            models.Index(fields=['risk_score', 'period_start']),
        ]
    
    def __str__(self):
        return f"{self.bookmaker.user.username} - {self.get_period_display()} ({self.period_start.date()})"
    
    @property
    def win_rate(self):
        """Tính tỷ lệ thắng"""
        if self.bets_placed > 0:
            return (self.bets_won / self.bets_placed) * 100
        return 0
    
    @property
    def roi(self):
        """Tính Return on Investment"""
        if self.total_stake > 0:
            return ((self.total_return - self.total_stake) / self.total_stake) * 100
        return 0
    
    def save(self, *args, **kwargs):
        # Tự động tính toán các giá trị
        if self.total_stake > 0:
            self.gross_margin = ((self.total_return - self.total_stake) / self.total_stake) * 100
        
        super().save(*args, **kwargs)
