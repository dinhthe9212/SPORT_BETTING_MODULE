from rest_framework import serializers
from .models import Sport, Team, Match, MatchEvent, SportsDataProvider

class SportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sport
        fields = '__all__'

class TeamSerializer(serializers.ModelSerializer):
    sport = SportSerializer(read_only=True)
    
    class Meta:
        model = Team
        fields = '__all__'

class MatchEventSerializer(serializers.ModelSerializer):
    team = TeamSerializer(read_only=True)
    event_type_display = serializers.CharField(source='get_event_type_display', read_only=True)
    
    class Meta:
        model = MatchEvent
        fields = '__all__'

class MatchSerializer(serializers.ModelSerializer):
    home_team = TeamSerializer(read_only=True)
    away_team = TeamSerializer(read_only=True)
    sport = SportSerializer(read_only=True)
    events = MatchEventSerializer(many=True, read_only=True)
    
    class Meta:
        model = Match
        fields = '__all__'

class MatchUpdateSerializer(serializers.ModelSerializer):
    """Serializer để cập nhật thông tin trận đấu"""
    
    class Meta:
        model = Match
        fields = [
            'score_home', 'score_away', 'current_minute',
            'possession_home', 'possession_away',
            'shots_on_target_home', 'shots_on_target_away',
            'corners_home', 'corners_away'
        ]

class MatchEventCreateSerializer(serializers.ModelSerializer):
    """Serializer để tạo sự kiện mới"""
    
    class Meta:
        model = MatchEvent
        fields = [
            'match', 'event_type', 'minute', 'team', 'player_name',
            'description', 'additional_data', 'requires_market_suspension',
            'suspension_duration'
        ]
    
    def validate(self, data):
        """Validate dữ liệu sự kiện"""
        match = data.get('match')
        minute = data.get('minute')
        
        if match and minute:
            if match.status != 'LIVE':
                raise serializers.ValidationError("Chỉ có thể thêm sự kiện cho trận đấu đang diễn ra")
            
            if minute < 0 or minute > 120:
                raise serializers.ValidationError("Phút phải trong khoảng 0-120")
        
        return data

class SportsDataProviderSerializer(serializers.ModelSerializer):
    supported_sports = SportSerializer(many=True, read_only=True)
    
    class Meta:
        model = SportsDataProvider
        fields = '__all__'

class WebhookEventSerializer(serializers.Serializer):
    """Serializer để xử lý webhook events từ sports data provider"""
    
    event_type = serializers.CharField(help_text='Loại sự kiện')
    match_id = serializers.CharField(help_text='ID trận đấu từ provider')
    minute = serializers.IntegerField(help_text='Phút xảy ra sự kiện')
    team_id = serializers.CharField(help_text='ID đội bóng')
    player_name = serializers.CharField(required=False, allow_blank=True, help_text='Tên cầu thủ')
    description = serializers.CharField(required=False, allow_blank=True, help_text='Mô tả sự kiện')
    additional_data = serializers.JSONField(required=False, default=dict, help_text='Dữ liệu bổ sung')
    
    # Market suspension flags
    requires_suspension = serializers.BooleanField(default=False, help_text='Có cần tạm dừng thị trường không')
    suspension_duration = serializers.IntegerField(default=30, help_text='Thời gian tạm dừng (giây)')
    
    def validate(self, data):
        """Validate webhook data"""
        if data.get('event_type') not in ['GOAL', 'RED_CARD', 'YELLOW_CARD', 'SUBSTITUTION', 'INJURY', 'PENALTY']:
            raise serializers.ValidationError("Loại sự kiện không hợp lệ")
        
        if data.get('minute', 0) < 0:
            raise serializers.ValidationError("Phút không thể âm")
        
        return data

class LiveScoreUpdateSerializer(serializers.Serializer):
    """Serializer để cập nhật tỷ số trận đấu"""
    
    match_id = serializers.CharField(help_text='ID trận đấu từ provider')
    score_home = serializers.IntegerField(min_value=0, help_text='Tỷ số đội nhà')
    score_away = serializers.IntegerField(min_value=0, help_text='Tỷ số đội khách')
    current_minute = serializers.IntegerField(min_value=0, max_value=120, help_text='Phút hiện tại')
    
    # Live statistics
    possession_home = serializers.IntegerField(min_value=0, max_value=100, required=False, help_text='Tỷ lệ kiểm soát bóng đội nhà (%)')
    possession_away = serializers.IntegerField(min_value=0, max_value=100, required=False, help_text='Tỷ lệ kiểm soát bóng đội khách (%)')
    shots_on_target_home = serializers.IntegerField(min_value=0, required=False, help_text='Sút trúng đích đội nhà')
    shots_on_target_away = serializers.IntegerField(min_value=0, required=False, help_text='Sút trúng đích đội khách')
    corners_home = serializers.IntegerField(min_value=0, required=False, help_text='Phạt góc đội nhà')
    corners_away = serializers.IntegerField(min_value=0, required=False, help_text='Phạt góc đội khách')
    
    def validate(self, data):
        """Validate tỷ số và thống kê"""
        if data.get('possession_home', 0) + data.get('possession_away', 0) != 100:
            if data.get('possession_home') and data.get('possession_away'):
                raise serializers.ValidationError("Tổng tỷ lệ kiểm soát bóng phải bằng 100%")
        
        return data


