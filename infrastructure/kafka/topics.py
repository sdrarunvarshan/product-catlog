"""
Kafka topic definitions for the e-commerce microservices.

This file defines the Kafka topics used for event-driven communication
between services. Topics are created automatically by the services,
but this serves as documentation of the event schema.
"""

# Order Service topics
ORDER_CREATED_TOPIC = "order.created"

# Payment Service topics
PAYMENT_COMPLETED_TOPIC = "payment.completed"
PAYMENT_FAILED_TOPIC = "payment.failed"

# Event schemas
EVENT_SCHEMAS = {
    ORDER_CREATED_TOPIC: {
        "event_type": "order.created",
        "event_id": "UUID",
        "order_id": "UUID",
        "customer_id": "UUID",
        "amount": "float",
        "timestamp": "ISO8601"
    },
    PAYMENT_COMPLETED_TOPIC: {
        "event_type": "payment.completed",
        "event_id": "UUID",
        "order_id": "UUID",
        "customer_id": "UUID",
        "amount": "float",
        "transaction_reference": "string",
        "timestamp": "ISO8601"
    },
    PAYMENT_FAILED_TOPIC: {
        "event_type": "payment.failed",
        "event_id": "UUID",
        "order_id": "UUID",
        "customer_id": "UUID",
        "amount": "float",
        "transaction_reference": "string",
        "timestamp": "ISO8601"
    }
}
