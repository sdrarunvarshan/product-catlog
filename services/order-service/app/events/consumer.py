import json
import asyncio
from uuid import UUID
from aiokafka import AIOKafkaConsumer
from app.core.config import get_settings
from app.repositories.order_repository import OrderRepository
from app.models.order import OrderStatus
from sqlalchemy.ext.asyncio import AsyncSession

settings = get_settings()


class KafkaEventConsumer:
    """Kafka event consumer for processing payment events."""

    def __init__(self, db_session_factory):
        self.consumer: AIOKafkaConsumer = None
        self.db_session_factory = db_session_factory
        self.running = False

    async def start(self):
        """Start the Kafka consumer."""
        self.consumer = AIOKafkaConsumer(
            settings.KAFKA_PAYMENT_COMPLETED_TOPIC,
            settings.KAFKA_PAYMENT_FAILED_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            group_id="order-service-group"
        )
        await self.consumer.start()
        self.running = True
        asyncio.create_task(self._consume_events())

    async def stop(self):
        """Stop the Kafka consumer."""
        self.running = False
        if self.consumer:
            await self.consumer.stop()

    async def _consume_events(self):
        """Consume events from Kafka topics."""
        while self.running:
            try:
                async for message in self.consumer:
                    await self._process_message(message)
            except Exception as e:
                print(f"Error consuming message: {e}")
                await asyncio.sleep(1)

    async def _process_message(self, message):
        """Process a single Kafka message."""
        event = message.value
        event_type = event.get("event_type")
        order_id = event.get("order_id")

        if not order_id:
            return

        async with self.db_session_factory() as db:
            order_repo = OrderRepository(db)

            if event_type == "payment.completed":
                await order_repo.update_order_status(
                    UUID(order_id),
                    OrderStatus.CONFIRMED
                )
                print(f"Order {order_id} confirmed after successful payment")

            elif event_type == "payment.failed":
                await order_repo.update_order_status(
                    UUID(order_id),
                    OrderStatus.PAYMENT_FAILED
                )
                print(f"Order {order_id} marked as payment failed")
