from django.db import models
from django.utils import timezone

class Sport(models.Model):
    """Model quản lý các môn thể thao"""
    
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
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=SPORT_CATEGORIES, default='BALL_SPORTS')
    is_active = models.BooleanField(default=True)
    
    # Sport-specific settings
    has_teams = models.BooleanField(default=True, help_text='Môn thể thao có đội hình không')
    has_individual_players = models.BooleanField(default=False, help_text='Môn thể thao có vận động viên cá nhân không')
    has_rounds = models.BooleanField(default=False, help_text='Môn thể thao có rounds không')
    has_sets = models.BooleanField(default=False, help_text='Môn thể thao có sets không')
    has_periods = models.BooleanField(default=False, help_text='Môn thể thao có periods không')
    
    # Betting configuration
    min_odds = models.DecimalField(max_digits=5, decimal_places=2, default=1.01, help_text='Tỷ lệ cược tối thiểu')
    max_odds = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00, help_text='Tỷ lệ cược tối đa')
    max_stake = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00, help_text='Số tiền cược tối đa')
    
    # Popularity metrics
    popularity_score = models.IntegerField(default=50, help_text='Điểm phổ biến (1-100)')
    betting_volume = models.DecimalField(max_digits=15, decimal_places=2, default=0.00, help_text='Tổng khối lượng cược')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-popularity_score', 'name']
        verbose_name = 'Sport'
        verbose_name_plural = 'Sports'

    def __str__(self):
        return self.name
    
    def get_betting_stats(self):
        """Lấy thống kê cược cho môn thể thao"""
        return {
            'total_matches': self.matches.count(),
            'active_matches': self.matches.filter(status='LIVE').count(),
            'total_bets': sum(match.total_bets for match in self.matches.all()),
            'popularity': self.get_popularity_display()
        }

class Team(models.Model):
    """Model quản lý đội hình và vận động viên"""
    
    TEAM_TYPES = [
        ('CLUB', 'Câu lạc bộ'),
        ('NATIONAL', 'Đội tuyển quốc gia'),
        ('REGIONAL', 'Đội tuyển khu vực'),
        ('INDIVIDUAL', 'Vận động viên cá nhân'),
    ]
    
    name = models.CharField(max_length=100)
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='teams')
    team_type = models.CharField(max_length=20, choices=TEAM_TYPES, default='CLUB')
    country = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    logo_url = models.URLField(blank=True, null=True)
    
    # Team details
    founded_year = models.IntegerField(blank=True, null=True)
    home_venue = models.CharField(max_length=255, blank=True, null=True)
    capacity = models.IntegerField(blank=True, null=True)
    
    # Performance metrics
    ranking = models.IntegerField(blank=True, null=True)
    points = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    draws = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    
    # Betting stats
    total_bets = models.IntegerField(default=0)
    total_stake = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('name', 'sport')
        ordering = ['-points', '-wins', 'name']
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'

    def __str__(self):
        return f"{self.name} ({self.sport.name})"
    
    def update_stats(self, result):
        """Cập nhật thống kê đội bóng"""
        if result == 'WIN':
            self.wins += 1
            self.points += 3
        elif result == 'DRAW':
            self.draws += 1
            self.points += 1
        elif result == 'LOSS':
            self.losses += 1
        self.save()

class Match(models.Model):
    """Model quản lý trận đấu"""
    
    MATCH_STATUSES = [
        ('SCHEDULED', 'Đã lên lịch'),
        ('LIVE', 'Đang diễn ra'),
        ('FINISHED', 'Đã kết thúc'),
        ('CANCELLED', 'Đã hủy'),
        ('POSTPONED', 'Đã hoãn'),
        ('SUSPENDED', 'Tạm dừng'),
    ]
    
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='matches')
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches')
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=MATCH_STATUSES, default='SCHEDULED')
    
    # Scores
    score_home = models.IntegerField(blank=True, null=True)
    score_away = models.IntegerField(blank=True, null=True)
    
    # Extended scores for different sports
    half_time_score_home = models.IntegerField(blank=True, null=True)
    half_time_score_away = models.IntegerField(blank=True, null=True)
    
    # Set scores (Tennis, Volleyball)
    sets_home = models.IntegerField(default=0)
    sets_away = models.IntegerField(default=0)
    
    # Period scores (Basketball, American Football)
    period_scores = models.JSONField(default=dict, help_text='Điểm từng hiệp')
    
    # Match details
    venue = models.CharField(max_length=255, blank=True, null=True)
    external_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    competition = models.CharField(max_length=255, blank=True, null=True)
    season = models.CharField(max_length=100, blank=True, null=True)
    
    # Live match data
    current_minute = models.IntegerField(default=0, help_text='Phút hiện tại của trận đấu')
    current_period = models.CharField(max_length=20, default='1H', help_text='Hiệp hiện tại')
    
    # Possession and stats
    possession_home = models.IntegerField(default=50, help_text='Tỷ lệ kiểm soát bóng đội nhà (%)')
    possession_away = models.IntegerField(default=50, help_text='Tỷ lệ kiểm soát bóng đội khách (%)')
    shots_on_target_home = models.IntegerField(default=0, help_text='Sút trúng đích đội nhà')
    shots_on_target_away = models.IntegerField(default=0, help_text='Sút trúng đích đội khách')
    corners_home = models.IntegerField(default=0, help_text='Phạt góc đội nhà')
    corners_away = models.IntegerField(default=0, help_text='Phạt góc đội khách')
    
    # Market suspension status
    is_market_suspended = models.BooleanField(default=False, help_text='Thị trường cược có bị tạm dừng không')
    suspension_reason = models.TextField(blank=True, null=True, help_text='Lý do tạm dừng thị trường')
    suspended_at = models.DateTimeField(blank=True, null=True, help_text='Thời điểm tạm dừng')
    resumed_at = models.DateTimeField(blank=True, null=True, help_text='Thời điểm khôi phục')
    
    # Betting stats
    total_bets = models.IntegerField(default=0)
    total_stake = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    average_odds = models.DecimalField(max_digits=5, decimal_places=2, default=2.00)
    
    # Timestamps
    last_event_update = models.DateTimeField(blank=True, null=True, help_text='Lần cập nhật sự kiện cuối')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_time']
        verbose_name = 'Match'
        verbose_name_plural = 'Matches'

    def __str__(self):
        return f"{self.home_team.name} vs {self.away_team.name} ({self.sport.name})"
    
    def suspend_market(self, reason=""):
        """Tạm dừng thị trường cược"""
        self.is_market_suspended = True
        self.suspension_reason = reason
        self.suspended_at = timezone.now()
        self.save()
    
    def resume_market(self):
        """Khôi phục thị trường cược"""
        self.is_market_suspended = False
        self.suspension_reason = ""
        self.resumed_at = timezone.now()
        self.save()
    
    def update_score(self, home_score, away_score, period='FULL'):
        """Cập nhật tỷ số trận đấu"""
        if period == 'FULL':
            self.score_home = home_score
            self.score_away = away_score
        elif period == 'HALF':
            self.half_time_score_home = home_score
            self.half_time_score_away = away_score
        
        self.last_event_update = timezone.now()
        self.save()
    
    def get_match_summary(self):
        """Lấy tóm tắt trận đấu"""
        return {
            'status': self.get_status_display(),
            'score': f"{self.score_home or 0} - {self.score_away or 0}",
            'time': self.current_minute if self.status == 'LIVE' else None,
            'venue': self.venue,
            'total_bets': self.total_bets,
            'total_stake': self.total_stake
        }

class MatchEvent(models.Model):
    """Model lưu trữ các sự kiện trong trận đấu"""
    
    EVENT_TYPES = [
        # Football events
        ('GOAL', 'Bàn thắng'),
        ('RED_CARD', 'Thẻ đỏ'),
        ('YELLOW_CARD', 'Thẻ vàng'),
        ('SUBSTITUTION', 'Thay người'),
        ('INJURY', 'Chấn thương'),
        ('PENALTY', 'Phạt đền'),
        ('FREE_KICK', 'Đá phạt trực tiếp'),
        ('CORNER', 'Phạt góc'),
        ('FOUL', 'Lỗi'),
        
        # Basketball events
        ('THREE_POINTER', '3 điểm'),
        ('TWO_POINTER', '2 điểm'),
        ('FREE_THROW', 'Ném phạt'),
        ('REBOUND', 'Bắt bóng bật bảng'),
        ('ASSIST', 'Kiến tạo'),
        ('BLOCK', 'Chặn bóng'),
        ('STEAL', 'Cướp bóng'),
        
        # Tennis events
        ('ACE', 'Giao bóng trực tiếp'),
        ('DOUBLE_FAULT', 'Lỗi giao bóng kép'),
        ('BREAK_POINT', 'Điểm break'),
        ('SET_WIN', 'Thắng set'),
        
        # Other sports
        ('ROUND_WIN', 'Thắng round'),
        ('PERIOD_WIN', 'Thắng hiệp'),
        ('RACE_WIN', 'Thắng cuộc đua'),
        ('OTHER', 'Sự kiện khác'),
    ]
    
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='events')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    minute = models.IntegerField(help_text='Phút xảy ra sự kiện')
    
    # Event details
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='match_events')
    player_name = models.CharField(max_length=100, blank=True, null=True, help_text='Tên cầu thủ liên quan')
    description = models.TextField(blank=True, null=True, help_text='Mô tả chi tiết sự kiện')
    
    # Additional data
    additional_data = models.JSONField(default=dict, help_text='Dữ liệu bổ sung (ví dụ: vị trí, loại lỗi)')
    
    # Market impact
    requires_market_suspension = models.BooleanField(default=False, help_text='Sự kiện có cần tạm dừng thị trường không')
    suspension_duration = models.IntegerField(default=0, help_text='Thời gian tạm dừng (giây)')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['minute', 'created_at']
        verbose_name = 'Match Event'
        verbose_name_plural = 'Match Events'
    
    def __str__(self):
        return f"{self.match} - {self.get_event_type_display()} at {self.minute}'"
    
    def should_suspend_market(self):
        """Kiểm tra xem sự kiện có cần tạm dừng thị trường không"""
        return self.requires_market_suspension and self.event_type in ['GOAL', 'RED_CARD', 'PENALTY']

class SportsDataProvider(models.Model):
    """Model quản lý nhà cung cấp dữ liệu thể thao"""
    
    PROVIDER_TYPES = [
        ('LIVE_SCORES', 'Cập nhật tỷ số trực tiếp'),
        ('STATISTICS', 'Thống kê chi tiết'),
        ('ODDS', 'Tỷ lệ cược'),
        ('NEWS', 'Tin tức thể thao'),
        ('COMPREHENSIVE', 'Toàn diện'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    provider_type = models.CharField(max_length=20, choices=PROVIDER_TYPES, default='COMPREHENSIVE')
    api_endpoint = models.URLField(help_text='Endpoint API của provider')
    api_key = models.CharField(max_length=255, help_text='API key để xác thực')
    webhook_url = models.URLField(blank=True, null=True, help_text='Webhook URL để nhận updates')
    
    # Configuration
    is_active = models.BooleanField(default=True)
    update_frequency = models.IntegerField(default=30, help_text='Tần suất cập nhật (giây)')
    supported_sports = models.ManyToManyField(Sport, help_text='Các môn thể thao được hỗ trợ')
    
    # Quality metrics
    data_accuracy = models.DecimalField(max_digits=3, decimal_places=2, default=0.95, help_text='Độ chính xác dữ liệu (0-1)')
    update_speed = models.IntegerField(default=30, help_text='Tốc độ cập nhật (giây)')
    coverage_rate = models.DecimalField(max_digits=3, decimal_places=2, default=0.90, help_text='Tỷ lệ bao phủ (0-1)')
    
    # Status
    last_successful_update = models.DateTimeField(blank=True, null=True)
    last_error = models.TextField(blank=True, null=True)
    error_count = models.IntegerField(default=0)
    consecutive_failures = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-data_accuracy', '-coverage_rate']
        verbose_name = 'Sports Data Provider'
        verbose_name_plural = 'Sports Data Providers'
    
    def __str__(self):
        return self.name
    
    def get_performance_score(self):
        """Tính điểm hiệu suất của provider"""
        accuracy_weight = 0.4
        speed_weight = 0.3
        coverage_weight = 0.3
        
        speed_score = max(0, 1 - (self.update_speed / 300))  # 300s = 5 phút là tối đa
        performance_score = (
            self.data_accuracy * accuracy_weight +
            speed_score * speed_weight +
            self.coverage_rate * coverage_weight
        )
        return round(performance_score, 3)

class SportStatistics(models.Model):
    """Model lưu trữ thống kê chi tiết cho từng môn thể thao"""
    
    sport = models.OneToOneField(Sport, on_delete=models.CASCADE, related_name='statistics')
    
    # Match statistics
    total_matches = models.IntegerField(default=0)
    total_goals = models.IntegerField(default=0)
    total_cards = models.IntegerField(default=0)
    
    # Betting statistics
    total_bets_placed = models.IntegerField(default=0)
    total_stake_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    average_odds = models.DecimalField(max_digits=5, decimal_places=2, default=2.00)
    
    # Popularity metrics
    daily_active_users = models.IntegerField(default=0)
    weekly_active_users = models.IntegerField(default=0)
    monthly_active_users = models.IntegerField(default=0)
    
    # Timestamps
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Sport Statistics'
        verbose_name_plural = 'Sport Statistics'
    
    def __str__(self):
        return f"Statistics for {self.sport.name}"
    
    def update_match_stats(self, match):
        """Cập nhật thống kê từ trận đấu"""
        self.total_matches += 1
        if match.score_home is not None and match.score_away is not None:
            self.total_goals += match.score_home + match.score_away
        self.save()
