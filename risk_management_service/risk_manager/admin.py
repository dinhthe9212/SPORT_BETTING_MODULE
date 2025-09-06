from django.contrib import admin
from .models import (
    PriceVolatilityMonitor, MarketActivityMonitor, TradingSuspension,
    RiskConfiguration, RiskAlert, RiskMetrics, RiskAuditLog
)

# ============================================================================
# P2P MARKETPLACE RISK MANAGEMENT ADMIN
# ============================================================================

@admin.register(PriceVolatilityMonitor)
class PriceVolatilityMonitorAdmin(admin.ModelAdmin):
    list_display = ('bet_slip_id', 'market_identifier', 'price_change_percentage', 
                   'severity_level', 'detection_time', 'resolved')
    list_filter = ('severity_level', 'resolved', 'detection_time')
    search_fields = ('bet_slip_id', 'market_identifier')
    readonly_fields = ('id', 'detection_time', 'volatility_score')
    ordering = ('-detection_time',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('bet_slip_id', 'market_identifier')
        }),
        ('Price Data', {
            'fields': ('original_price', 'current_price', 'price_change_percentage', 'volatility_score')
        }),
        ('Analysis', {
            'fields': ('severity_level', 'resolved', 'resolution_notes')
        }),
        ('Metadata', {
            'fields': ('detection_time', 'resolved_at', 'metadata'),
            'classes': ('collapse',)
        })
    )

@admin.register(MarketActivityMonitor)
class MarketActivityMonitorAdmin(admin.ModelAdmin):
    list_display = ('activity_type', 'market_identifier', 'user_id', 
                   'severity_level', 'confidence_score', 'detected_at', 'resolved')
    list_filter = ('activity_type', 'severity_level', 'resolved', 'detected_at')
    search_fields = ('market_identifier', 'user_id', 'description')
    readonly_fields = ('id', 'detected_at')
    ordering = ('-detected_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('activity_type', 'market_identifier', 'user_id')
        }),
        ('Detection Details', {
            'fields': ('description', 'severity_level', 'confidence_score')
        }),
        ('Related Data', {
            'fields': ('related_orders', 'volume_data', 'price_data'),
            'classes': ('collapse',)
        }),
        ('Resolution', {
            'fields': ('resolved', 'resolved_at', 'resolved_by', 'resolution_notes')
        }),
        ('Metadata', {
            'fields': ('detected_at',)
        })
    )

@admin.register(TradingSuspension)
class TradingSuspensionAdmin(admin.ModelAdmin):
    list_display = ('suspension_type', 'reason', 'status', 'suspended_at', 
                   'suspended_by', 'expires_at')
    list_filter = ('suspension_type', 'reason', 'status', 'suspended_at')
    search_fields = ('description', 'suspended_by', 'sport_id', 'market_identifier')
    readonly_fields = ('id', 'suspended_at', 'lifted_at')
    ordering = ('-suspended_at',)
    
    fieldsets = (
        ('Suspension Details', {
            'fields': ('suspension_type', 'reason', 'description')
        }),
        ('Scope', {
            'fields': ('sport_id', 'market_identifier', 'user_id', 'event_id')
        }),
        ('Timing', {
            'fields': ('suspended_at', 'suspended_by', 'expires_at')
        }),
        ('Status', {
            'fields': ('status', 'lifted_at', 'lifted_by')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status != 'ACTIVE':
            return self.readonly_fields + ('suspension_type', 'reason', 'description')
        return self.readonly_fields

@admin.register(RiskConfiguration)
class RiskConfigurationAdmin(admin.ModelAdmin):
    list_display = ('config_key', 'config_type', 'is_active', 'updated_at', 'updated_by')
    list_filter = ('config_type', 'is_active', 'updated_at')
    search_fields = ('config_key', 'description')
    readonly_fields = ('id', 'created_at', 'updated_at')
    ordering = ('config_type', 'config_key')
    
    fieldsets = (
        ('Configuration', {
            'fields': ('config_type', 'config_key', 'config_value')
        }),
        ('Details', {
            'fields': ('description', 'is_active', 'updated_by')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at')
        })
    )

@admin.register(RiskAlert)
class RiskAlertAdmin(admin.ModelAdmin):
    list_display = ('alert_type', 'severity', 'title', 'status', 'created_at', 
                   'acknowledged_by', 'resolved_by')
    list_filter = ('alert_type', 'severity', 'status', 'created_at')
    search_fields = ('title', 'message', 'acknowledged_by', 'resolved_by')
    readonly_fields = ('id', 'created_at', 'acknowledged_at', 'resolved_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Alert Information', {
            'fields': ('alert_type', 'severity', 'title', 'message')
        }),
        ('Related Data', {
            'fields': ('related_data', 'affected_users', 'affected_markets'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'acknowledged_at', 'acknowledged_by', 
                      'resolved_at', 'resolved_by', 'resolution_notes')
        }),
        ('Metadata', {
            'fields': ('created_at',)
        })
    )
    
    def get_readonly_fields(self, request, obj=None):
        if obj and obj.status == 'RESOLVED':
            return self.readonly_fields + ('alert_type', 'severity', 'title', 'message')
        return self.readonly_fields

@admin.register(RiskMetrics)
class RiskMetricsAdmin(admin.ModelAdmin):
    list_display = ('metric_type', 'metric_name', 'metric_value', 
                   'timestamp', 'sport_id', 'market_identifier')
    list_filter = ('metric_type', 'timestamp', 'sport_id')
    search_fields = ('metric_name', 'sport_id', 'market_identifier')
    readonly_fields = ('id', 'timestamp')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Metric Information', {
            'fields': ('metric_type', 'metric_name', 'metric_value')
        }),
        ('Scope', {
            'fields': ('sport_id', 'market_identifier')
        }),
        ('Time Period', {
            'fields': ('timestamp', 'period_start', 'period_end')
        }),
        ('Metadata', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        })
    )

@admin.register(RiskAuditLog)
class RiskAuditLogAdmin(admin.ModelAdmin):
    list_display = ('action_type', 'user_id', 'timestamp', 'success', 
                   'related_object_type', 'ip_address')
    list_filter = ('action_type', 'success', 'timestamp')
    search_fields = ('action_description', 'user_id', 'ip_address')
    readonly_fields = ('id', 'timestamp')
    ordering = ('-timestamp',)
    date_hierarchy = 'timestamp'
    
    fieldsets = (
        ('Action Information', {
            'fields': ('action_type', 'action_description', 'success')
        }),
        ('User Information', {
            'fields': ('user_id', 'ip_address', 'user_agent')
        }),
        ('Related Object', {
            'fields': ('related_object_type', 'related_object_id')
        }),
        ('Details', {
            'fields': ('action_details', 'error_message'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('timestamp',)
        })
    )

# Customize admin site
admin.site.site_header = "Risk Management Administration"
admin.site.site_title = "Risk Management Admin Portal"
admin.site.index_title = "Welcome to Risk Management Administration"