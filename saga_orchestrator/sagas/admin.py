from django.contrib import admin
from .models import SagaTransaction, SagaStep, SagaEvent, SagaDefinition

@admin.register(SagaTransaction)
class SagaTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'saga_type', 'status', 'user_id', 'correlation_id', 'created_at']
    list_filter = ['saga_type', 'status', 'created_at']
    search_fields = ['correlation_id', 'user_id']
    readonly_fields = ['id', 'created_at', 'updated_at']

@admin.register(SagaStep)
class SagaStepAdmin(admin.ModelAdmin):
    list_display = ['id', 'saga_transaction', 'step_name', 'step_order', 'status', 'service_name']
    list_filter = ['status', 'service_name', 'step_type']
    search_fields = ['step_name', 'saga_transaction__correlation_id']
    readonly_fields = ['id', 'created_at']

@admin.register(SagaEvent)
class SagaEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'saga_transaction', 'event_type', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['saga_transaction__correlation_id', 'message']
    readonly_fields = ['id', 'created_at']

@admin.register(SagaDefinition)
class SagaDefinitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'saga_type', 'version', 'is_active', 'created_at']
    list_filter = ['saga_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

