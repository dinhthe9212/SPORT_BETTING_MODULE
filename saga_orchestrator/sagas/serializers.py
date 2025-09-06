from rest_framework import serializers
from .models import SagaTransaction, SagaStep, SagaEvent, SagaDefinition

class SagaStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = SagaStep
        fields = [
            'id', 'step_name', 'step_type', 'step_order', 'status',
            'service_name', 'service_endpoint', 'http_method',
            'request_data', 'response_data', 'error_message',
            'retry_count', 'max_retries', 'created_at', 'started_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'response_data', 'error_message', 'retry_count',
            'created_at', 'started_at', 'completed_at'
        ]

class SagaEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SagaEvent
        fields = [
            'id', 'event_type', 'event_data', 'message', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class SagaTransactionSerializer(serializers.ModelSerializer):
    steps = SagaStepSerializer(many=True, read_only=True)
    events = SagaEventSerializer(many=True, read_only=True)
    
    class Meta:
        model = SagaTransaction
        fields = [
            'id', 'saga_type', 'status', 'user_id', 'correlation_id',
            'input_data', 'context_data', 'result_data',
            'created_at', 'updated_at', 'started_at', 'completed_at', 'timeout_at',
            'error_message', 'retry_count', 'max_retries',
            'steps', 'events'
        ]
        read_only_fields = [
            'id', 'status', 'context_data', 'result_data',
            'created_at', 'updated_at', 'started_at', 'completed_at',
            'error_message', 'retry_count', 'steps', 'events'
        ]

class SagaStartRequestSerializer(serializers.Serializer):
    """Serializer for starting a new saga"""
    saga_type = serializers.ChoiceField(choices=SagaTransaction.SAGA_TYPES)
    user_id = serializers.IntegerField()
    input_data = serializers.JSONField()
    correlation_id = serializers.CharField(max_length=255, required=False)

class SagaDefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SagaDefinition
        fields = [
            'id', 'name', 'saga_type', 'description', 'workflow_definition',
            'timeout_seconds', 'max_retries', 'retry_delay_seconds',
            'is_active', 'version', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class SagaStatusSerializer(serializers.Serializer):
    """Serializer for saga status response"""
    saga_id = serializers.UUIDField()
    status = serializers.CharField()
    progress = serializers.DictField()
    current_step = serializers.CharField(required=False)
    error_message = serializers.CharField(required=False)

