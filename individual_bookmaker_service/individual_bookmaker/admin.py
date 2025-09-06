from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    IndividualBookmaker, RiskEducationTutorial, TutorialProgress,
    RiskAlert, BestPractice, BookmakerPerformance
)


@admin.register(IndividualBookmaker)
class IndividualBookmakerAdmin(admin.ModelAdmin):
    """Admin interface cho Individual Bookmaker"""
    list_display = [
        'id', 'user_link', 'status', 'experience_level', 'risk_tolerance',
        'total_events_created', 'total_bets_placed', 'success_rate', 'total_profit_loss',
        'created_at'
    ]
    list_filter = [
        'status', 'experience_level', 'risk_tolerance', 'created_at', 'updated_at'
    ]
    search_fields = ['user__username', 'user__email', 'bookmaker_id']
    readonly_fields = ['id', 'bookmaker_id', 'created_at', 'updated_at', 'last_activity']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'bookmaker_id', 'status', 'experience_level')
        }),
        ('Risk Management', {
            'fields': ('risk_tolerance', 'max_bet_amount', 'preferred_sports')
        }),
        ('Performance Metrics', {
            'fields': ('total_events_created', 'total_bets_placed', 'total_profit_loss', 'success_rate')
        }),
        ('Education Settings', {
            'fields': ('education_enabled', 'auto_risk_alerts', 'tutorial_reminders')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_activity'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
    
    def user_link(self, obj):
        """Tạo link đến user"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'


@admin.register(RiskEducationTutorial)
class RiskEducationTutorialAdmin(admin.ModelAdmin):
    """Admin interface cho Risk Education Tutorial"""
    list_display = [
        'id', 'title', 'category', 'difficulty_level', 'estimated_duration',
        'is_active', 'created_at'
    ]
    list_filter = [
        'category', 'difficulty_level', 'is_active', 'created_at'
    ]
    search_fields = ['title', 'description', 'content']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'content')
        }),
        ('Classification', {
            'fields': ('category', 'difficulty_level', 'estimated_duration')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)
    
    def tutorial_stats(self, obj):
        """Hiển thị thống kê tutorial"""
        total_users = TutorialProgress.objects.filter(tutorial=obj).count()
        completed_users = TutorialProgress.objects.filter(
            tutorial=obj, is_completed=True
        ).count()
        
        if total_users > 0:
            completion_rate = (completed_users / total_users) * 100
            return f"{completed_users}/{total_users} ({completion_rate:.1f}%)"
        return "0/0 (0%)"
    
    tutorial_stats.short_description = 'Completion Stats'


@admin.register(TutorialProgress)
class TutorialProgressAdmin(admin.ModelAdmin):
    """Admin interface cho Tutorial Progress"""
    list_display = [
        'id', 'user_link', 'tutorial_title', 'status', 'progress_percentage',
        'is_completed', 'completed_at', 'created_at'
    ]
    list_filter = [
        'status', 'created_at', 'updated_at'
    ]
    search_fields = ['user__username', 'user__email', 'tutorial__title']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'tutorial')
        }),
        ('Progress', {
            'fields': ('status', 'progress_percentage', 'time_spent', 'quiz_score', 'points_earned')
        }),
        ('Completion', {
            'fields': ('is_completed', 'started_at', 'completed_at', 'attempts_count')
        }),
        ('Feedback', {
            'fields': ('notes', 'rating', 'feedback')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('tutorial')
    
    def user_link(self, obj):
        """Tạo link đến user"""
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    user_link.admin_order_field = 'user__username'
    
    def tutorial_title(self, obj):
        """Hiển thị title của tutorial"""
        return obj.tutorial.title if obj.tutorial else '-'
    tutorial_title.short_description = 'Tutorial'
    tutorial_title.admin_order_field = 'tutorial__title'
    
    def is_completed(self, obj):
        """Hiển thị trạng thái hoàn thành"""
        return obj.status == 'COMPLETED'
    is_completed.boolean = True
    is_completed.short_description = 'Completed'


@admin.register(RiskAlert)
class RiskAlertAdmin(admin.ModelAdmin):
    """Admin interface cho Risk Alert"""
    list_display = [
        'id', 'bookmaker_link', 'alert_type', 'category', 'title',
        'status', 'risk_score', 'created_at'
    ]
    list_filter = [
        'alert_type', 'category', 'status', 'priority', 'created_at'
    ]
    search_fields = ['bookmaker__user__username', 'title', 'message']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('bookmaker', 'alert_type', 'category', 'title', 'message', 'description')
        }),
        ('Risk Data', {
            'fields': ('risk_score', 'risk_data', 'recommended_actions')
        }),
        ('Settings', {
            'fields': ('priority', 'auto_resolve', 'expires_at')
        }),
        ('Status', {
            'fields': ('status', 'acknowledged_at', 'acknowledged_by', 'resolved_at', 'resolution_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('bookmaker__user')
    
    def bookmaker_link(self, obj):
        """Tạo link đến bookmaker"""
        if obj.bookmaker and obj.bookmaker.user:
            url = reverse('admin:individual_bookmaker_individualbookmaker_change', args=[obj.bookmaker.id])
            return format_html('<a href="{}">{}</a>', url, obj.bookmaker.user.username)
        return '-'
    bookmaker_link.short_description = 'Bookmaker'
    bookmaker_link.admin_order_field = 'bookmaker__user__username'
    
    def alert_summary(self, obj):
        """Hiển thị summary của alert"""
        return format_html(
            '<div style="max-width: 300px;">'
            '<strong>{}</strong><br/>'
            '<small style="color: #666;">{}</small>'
            '</div>',
            obj.title,
            obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
        )
    alert_summary.short_description = 'Alert Summary'


@admin.register(BestPractice)
class BestPracticeAdmin(admin.ModelAdmin):
    """Admin interface cho Best Practice"""
    list_display = [
        'id', 'title', 'category', 'difficulty_level',
        'is_active', 'created_at'
    ]
    list_filter = [
        'category', 'difficulty_level', 'is_active', 'created_at'
    ]
    search_fields = ['title', 'description', 'content']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'content')
        }),
        ('Classification', {
            'fields': ('category', 'difficulty_level')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(BookmakerPerformance)
class BookmakerPerformanceAdmin(admin.ModelAdmin):
    """Admin interface cho Bookmaker Performance"""
    list_display = [
        'id', 'bookmaker_link', 'period', 'period_start',
        'total_profit_loss', 'win_rate', 'risk_score', 'created_at'
    ]
    list_filter = [
        'period', 'period_start', 'created_at'
    ]
    search_fields = ['bookmaker__user__username', 'notes']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('bookmaker', 'period', 'period_start', 'period_end')
        }),
        ('Activity Statistics', {
            'fields': ('events_created', 'bets_placed', 'bets_won', 'bets_lost')
        }),
        ('Financial Statistics', {
            'fields': ('total_stake', 'total_return', 'total_profit_loss', 'gross_margin')
        }),
        ('Risk Statistics', {
            'fields': ('max_drawdown', 'risk_score', 'volatility')
        }),
        ('Education Statistics', {
            'fields': ('tutorials_completed', 'education_score', 'risk_alerts_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('bookmaker__user')
    
    def bookmaker_link(self, obj):
        """Tạo link đến bookmaker"""
        if obj.bookmaker and obj.bookmaker.user:
            url = reverse('admin:individual_bookmaker_individualbookmaker_change', args=[obj.bookmaker.id])
            return format_html('<a href="{}">{}</a>', url, obj.bookmaker.user.username)
        return '-'
    bookmaker_link.short_description = 'Bookmaker'
    bookmaker_link.admin_order_field = 'bookmaker__user__username'
    
    def performance_indicator(self, obj):
        """Hiển thị indicator cho performance"""
        if obj.performance_score >= 80:
            color = 'green'
            text = 'Excellent'
        elif obj.performance_score >= 60:
            color = 'orange'
            text = 'Good'
        elif obj.performance_score >= 40:
            color = 'yellow'
            text = 'Fair'
        else:
            color = 'red'
            text = 'Poor'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, text
        )
    performance_indicator.short_description = 'Performance Level'


# Custom admin site configuration
admin.site.site_header = 'Individual Bookmaker Service Admin'
admin.site.site_title = 'Bookmaker Admin'
admin.site.index_title = 'Welcome to Individual Bookmaker Service Administration'

# Register custom admin actions
@admin.action(description='Mark selected alerts as read')
def mark_alerts_read(modeladmin, request, queryset):
    """Action để đánh dấu alerts đã đọc"""
    updated = queryset.update(is_read=True)
    modeladmin.message_user(
        request,
        f'{updated} alerts were successfully marked as read.'
    )

@admin.action(description='Activate selected tutorials')
def activate_tutorials(modeladmin, request, queryset):
    """Action để kích hoạt tutorials"""
    updated = queryset.update(is_active=True)
    modeladmin.message_user(
        request,
        f'{updated} tutorials were successfully activated.'
    )

@admin.action(description='Deactivate selected tutorials')
def deactivate_tutorials(modeladmin, request, queryset):
    """Action để vô hiệu hóa tutorials"""
    updated = queryset.update(is_active=False)
    modeladmin.message_user(
        request,
        f'{updated} tutorials were successfully deactivated.'
    )

# Thêm actions vào admin
RiskAlertAdmin.actions = [mark_alerts_read]
RiskEducationTutorialAdmin.actions = [activate_tutorials, deactivate_tutorials]
BestPracticeAdmin.actions = [activate_tutorials, deactivate_tutorials]
