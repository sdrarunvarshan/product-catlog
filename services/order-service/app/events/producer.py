import json
import uuid
from typing import Dict, Any
from aiokafka import AIOKafkaProducer
from app.core.config import get_settings

settings = get_settings()


class KafkaEventProducer:
    """Kafka event producer for publishing events."""

    def __init__(self):
        self.producer: AIOKafkaProducer = None

    async def start(self):
        """Start the Kafka producer."""
        self.producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        await self.producer.start()

    async def stop(self):
        """Stop the Kafka producer."""
        if self.producer:
            await self.producer.stop()

    async def publish_order_created(
        self,
        order_id: uuid.UUID,
        customer_id: uuid.UUID,
        total_amount: float
    ):
        """Publish an order.created event."""
        event = {
            "event_type": "order.created",
            "event_id": str(uuid.uuid4()),
            "order_id": str(order_id),
            "customer_id": str(customer_id),
            "amount": float(total_amount),
            "timestamp": self._get_timestamp()
        }
        await self.producer.send_and_wait(
            settings.KAFKA_ORDER_CREATED_TOPIC,
            value=event
        )

    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.utcnow().isoformat()


# Global producer instance
kafka_producer = KafkaEventProducer()
