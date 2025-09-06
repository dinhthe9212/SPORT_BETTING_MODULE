from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    IndividualBookmaker, RiskEducationTutorial, TutorialProgress,
    RiskAlert, BestPractice, BookmakerPerformance
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer cho User model"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class IndividualBookmakerSerializer(serializers.ModelSerializer):
    """Serializer cho Individual Bookmaker"""
    user = UserSerializer(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = IndividualBookmaker
        fields = [
            'id', 'user', 'user_id', 'status', 'risk_level', 'risk_score',
            'performance_score', 'total_bets', 'win_rate', 'total_profit',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_risk_score(self, value):
        """Validate risk score range"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Risk score must be between 0 and 100")
        return value
    
    def validate_performance_score(self, value):
        """Validate performance score range"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Performance score must be between 0 and 100")
        return value


class RiskEducationTutorialSerializer(serializers.ModelSerializer):
    """Serializer cho Risk Education Tutorial"""
    class Meta:
        model = RiskEducationTutorial
        fields = [
            'id', 'title', 'description', 'content', 'category',
            'difficulty_level', 'duration_minutes', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_duration_minutes(self, value):
        """Validate duration is positive"""
        if value <= 0:
            raise serializers.ValidationError("Duration must be positive")
        return value


class TutorialProgressSerializer(serializers.ModelSerializer):
    """Serializer cho Tutorial Progress"""
    tutorial = RiskEducationTutorialSerializer(read_only=True)
    tutorial_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = TutorialProgress
        fields = [
            'id', 'user_id', 'tutorial', 'tutorial_id', 'progress_percentage',
            'is_completed', 'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_progress_percentage(self, value):
        """Validate progress percentage range"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Progress percentage must be between 0 and 100")
        return value


class RiskAlertSerializer(serializers.ModelSerializer):
    """Serializer cho Risk Alert"""
    class Meta:
        model = RiskAlert
        fields = [
            'id', 'user_id', 'alert_type', 'severity', 'title', 'message',
            'is_read', 'read_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_severity(self, value):
        """Validate severity choices"""
        valid_severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        if value not in valid_severities:
            raise serializers.ValidationError(f"Severity must be one of: {valid_severities}")
        return value


class BestPracticeSerializer(serializers.ModelSerializer):
    """Serializer cho Best Practice"""
    class Meta:
        model = BestPractice
        fields = [
            'id', 'title', 'description', 'content', 'category',
            'difficulty_level', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class BookmakerPerformanceSerializer(serializers.ModelSerializer):
    """Serializer cho Bookmaker Performance"""
    class Meta:
        model = BookmakerPerformance
        fields = [
            'id', 'user_id', 'period', 'performance_type', 'performance_score',
            'metrics_data', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def validate_performance_score(self, value):
        """Validate performance score range"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Performance score must be between 0 and 100")
        return value


class DashboardDataSerializer(serializers.Serializer):
    """Serializer cho Dashboard data"""
    user_info = IndividualBookmakerSerializer()
    recent_alerts = RiskAlertSerializer(many=True)
    tutorial_progress = TutorialProgressSerializer(many=True)
    performance_summary = serializers.DictField()
    risk_overview = serializers.DictField()


class RiskOverviewSerializer(serializers.Serializer):
    """Serializer cho Risk Overview"""
    current_risk_level = serializers.CharField()
    risk_score = serializers.FloatField()
    risk_trend = serializers.CharField()
    recent_alerts = RiskAlertSerializer(many=True)
    recommendations = serializers.ListField(child=serializers.CharField())


class EducationProgressSerializer(serializers.Serializer):
    """Serializer cho Education Progress"""
    completed_tutorials = serializers.IntegerField()
    total_tutorials = serializers.IntegerField()
    progress_percentage = serializers.FloatField()
    current_tutorials = TutorialProgressSerializer(many=True)
    recommended_tutorials = RiskEducationTutorialSerializer(many=True)


class PerformanceAnalyticsSerializer(serializers.Serializer):
    """Serializer cho Performance Analytics"""
    overall_score = serializers.FloatField()
    trend_data = serializers.ListField()
    comparison_data = serializers.DictField()
    improvement_suggestions = serializers.ListField(child=serializers.CharField())


class AlertAcknowledgmentSerializer(serializers.Serializer):
    """Serializer cho Alert Acknowledgment"""
    alert_id = serializers.IntegerField()
    acknowledgment_note = serializers.CharField(required=False, allow_blank=True)


class TutorialCompletionSerializer(serializers.Serializer):
    """Serializer cho Tutorial Completion"""
    tutorial_id = serializers.IntegerField()
    completion_note = serializers.CharField(required=False, allow_blank=True)
    rating = serializers.IntegerField(required=False, min_value=1, max_value=5)


class WebhookRiskUpdateSerializer(serializers.Serializer):
    """Serializer cho Webhook Risk Update"""
    user_id = serializers.IntegerField()
    risk_level = serializers.CharField()
    risk_score = serializers.FloatField()
    timestamp = serializers.DateTimeField(required=False)
    source = serializers.CharField(required=False)


class HealthCheckSerializer(serializers.Serializer):
    """Serializer cho Health Check"""
    status = serializers.CharField()
    service = serializers.CharField()
    timestamp = serializers.DateTimeField()
    error = serializers.CharField(required=False)
