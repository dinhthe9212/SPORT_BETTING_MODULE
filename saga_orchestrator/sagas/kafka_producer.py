import json
import logging
from kafka import KafkaProducer as Producer
from django.conf import settings

logger = logging.getLogger(__name__)

class KafkaProducer:
    """Kafka producer for saga events"""
    
    def __init__(self):
        self.producer = None
        self._initialize_producer()
    
    def _initialize_producer(self):
        """Initialize Kafka producer"""
        try:
            self.producer = Producer(
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None,
                acks='all',
                retries=3,
                retry_backoff_ms=1000
            )
            logger.info("Kafka producer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            self.producer = None
    
    def publish_event(self, event_type, event_data, topic='saga_events'):
        """Publish event to Kafka"""
        if not self.producer:
            logger.warning("Kafka producer not available, skipping event publication")
            return
        
        try:
            message = {
                'event_type': event_type,
                'timestamp': event_data.get('timestamp'),
                'data': event_data
            }
            
            future = self.producer.send(
                topic,
                key=event_data.get('correlation_id'),
                value=message
            )
            
            # Wait for message to be sent
            future.get(timeout=10)
            logger.info(f"Published event {event_type} to topic {topic}")
            
        except Exception as e:
            logger.error(f"Failed to publish event to Kafka: {e}")
    
    def close(self):
        """Close Kafka producer"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")

