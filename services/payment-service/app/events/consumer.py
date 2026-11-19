import json
import asyncio
from uuid import UUID
from aiokafka import AIOKafkaConsumer
from app.core.config import get_settings
from app.services.payment_service import PaymentService
from app.events.producer import kafka_producer
from app.models.payment import PaymentStatus
from sqlalchemy.ext.asyncio import AsyncSession

settings = get_settings()


class KafkaEventConsumer:
    """Kafka event consumer for processing order events."""

    def __init__(self, db_session_factory):
        self.consumer: AIOKafkaConsumer = None
        self.db_session_factory = db_session_factory
        self.running = False

    async def start(self):
        """Start the Kafka consumer."""
        self.consumer = AIOKafkaConsumer(
            settings.KAFKA_ORDER_CREATED_TOPIC,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            group_id="payment-service-group"
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

        if event_type != "order.created":
            return

        order_id = event.get("order_id")
        customer_id = event.get("customer_id")
        amount = event.get("amount")

        if not all([order_id, customer_id, amount]):
            print(f"Invalid order.created event: {event}")
            return

        async with self.db_session_factory() as db:
            payment_service = PaymentService(db)

            # Process payment
            payment = await payment_service.process_payment(
                UUID(order_id),
                UUID(customer_id),
                amount
            )

            # Publish payment result event
            if payment.payment_status == PaymentStatus.SUCCESS:
                await kafka_producer.publish_payment_completed(
                    payment.order_id,
                    payment.customer_id,
                    payment.amount,
                    payment.transaction_reference
                )
                print(f"Payment successful for order {order_id}")
            else:
                await kafka_producer.publish_payment_failed(
                    payment.order_id,
                    payment.customer_id,
                    payment.amount,
                    payment.transaction_reference
                )
                print(f"Payment failed for order {order_id}")
