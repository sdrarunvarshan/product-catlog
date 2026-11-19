# E-Commerce Microservices Architecture

A production-style, event-driven e-commerce platform built with FastAPI, PostgreSQL, Apache Kafka, and Docker Compose. This project demonstrates a complete microservices architecture with authentication, product management, order processing, and payment handling.

## Table of Contents

- [Project Overview](#project-overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Database Design](#database-design)
- [Kafka Event Flow](#kafka-event-flow)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Sample Workflows](#sample-workflows)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Project Overview

This e-commerce platform consists of four independent microservices that communicate via REST APIs and Apache Kafka events:

- **Auth Service**: User registration, authentication, and JWT token management
- **Product Service**: Product catalog management with CRUD operations
- **Order Service**: Shopping cart and order management with event-driven payment processing
- **Payment Service**: Mock payment processing with event publishing

The architecture follows best practices including:
- Service isolation with separate databases
- Event-driven communication via Kafka
- JWT-based authentication
- Role-based authorization (CUSTOMER/ADMIN)
- Async/await patterns throughout
- Docker containerization

## Architecture

### Microservices

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Auth      │      │  Product    │      │   Order     │      │  Payment    │
│  Service    │      │  Service    │      │  Service    │      │  Service    │
│   Port 8001 │      │  Port 8002  │      │  Port 8003  │      │  Port 8004  │
└──────┬──────┘      └──────┬──────┘      └──────┬──────┘      └──────┬──────┘
       │                     │                     │                     │
       └─────────────────────┴─────────────────────┴─────────────────────┘
                                     │
                                     │
                               ┌─────▼─────┐
                               │  Kafka    │
                               │  (Events) │
                               └───────────┘
                                     │
                               ┌─────▼─────┐
                               │PostgreSQL │
                               │(4 Databases)│
                               └───────────┘
```

### Service Responsibilities

| Service | Port | Responsibilities |
|---------|------|------------------|
| Auth Service | 8001 | User registration, login, JWT tokens, role management |
| Product Service | 8002 | Product CRUD operations, stock management |
| Order Service | 8003 | Shopping cart, order creation, event publishing/consuming |
| Payment Service | 8004 | Mock payment processing, payment status tracking |

## Technology Stack

- **Python**: 3.12+
- **Web Framework**: FastAPI
- **ORM**: SQLAlchemy 2.0 (async)
- **Validation**: Pydantic v2
- **Database**: PostgreSQL
- **Migrations**: Alembic
- **Message Broker**: Apache Kafka (KRaft mode)
- **Kafka Client**: aiokafka
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Dependency Management**: uv
- **Containerization**: Docker & Docker Compose
- **Testing**: pytest, httpx

## Project Structure

```
ecommerce-microservices/
│
├── services/
│   ├── auth-service/          # Authentication microservice
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── api/v1/       # API routes
│   │   │   ├── services/     # Business logic
│   │   │   ├── repositories/  # Database operations
│   │   │   ├── models/       # SQLAlchemy models
│   │   │   ├── schemas/      # Pydantic schemas
│   │   │   ├── core/         # Config & security
│   │   │   └── db/           # Database session
│   │   ├── migrations/       # Alembic migrations
│   │   ├── seed.py           # Admin seed script
│   │   ├── alembic.ini
│   │   ├── pyproject.toml
│   │   └── Dockerfile
│   │
│   ├── product-service/       # Product catalog microservice
│   │   └── (similar structure)
│   │
│   ├── order-service/        # Order management microservice
│   │   ├── app/
│   │   │   └── events/       # Kafka producer/consumer
│   │   └── (similar structure)
│   │
│   └── payment-service/      # Payment processing microservice
│       ├── app/
│       │   └── events/       # Kafka producer/consumer
│       └── (similar structure)
│
├── infrastructure/
│   ├── kafka/
│   │   └── topics.py         # Kafka topic definitions
│   └── postgres/
│       └── init.sql          # Database initialization
│
├── tests/
│   ├── integration/          # Service-level tests
│   └── e2e/                  # End-to-end tests
│
├── docker-compose.yml        # Docker Compose configuration
├── .env.example              # Environment variables template
├── .gitignore
└── README.md
```

## Database Design

Each microservice has its own PostgreSQL database:

| Database | Purpose |
|----------|---------|
| `ecommerce_auth` | User accounts and authentication |
| `ecommerce_products` | Product catalog |
| `ecommerce_orders` | Orders and shopping carts |
| `ecommerce_payments` | Payment transactions |

### Key Database Principles

- **Separation of concerns**: Each service owns its database
- **No cross-service foreign keys**: Services communicate via events, not direct database access
- **UUID identifiers**: Used for entities shared between services
- **Decimal for money**: Monetary values use DECIMAL type, not floating-point
- **Timestamps**: All tables have created_at and updated_at fields

### Schema Highlights

**Users (Auth Service)**
- id (UUID)
- email (unique)
- hashed_password
- role (CUSTOMER/ADMIN)
- is_active

**Products (Product Service)**
- id (UUID)
- name
- description
- price (DECIMAL)
- stock_quantity
- is_active

**Orders (Order Service)**
- id (UUID)
- customer_id (UUID)
- total_amount (DECIMAL)
- status (PENDING_PAYMENT/CONFIRMED/PAYMENT_FAILED/CANCELLED)
- Order items with product snapshots

**Payments (Payment Service)**
- id (UUID)
- order_id (UUID)
- customer_id (UUID)
- amount (DECIMAL)
- payment_status (SUCCESS/FAILED)
- transaction_reference (unique)

## Kafka Event Flow

The platform uses Apache Kafka for asynchronous event-driven communication between services.

### Topics

- `order.created`: Published by Order Service when an order is created
- `payment.completed`: Published by Payment Service when payment succeeds
- `payment.failed`: Published by Payment Service when payment fails

### Event Flow

```
1. Customer adds products to cart
   ↓
2. Customer checks out
   ↓
3. Order Service creates order (PENDING_PAYMENT)
   ↓
4. Order Service publishes order.created event to Kafka
   ↓
5. Payment Service consumes order.created event
   ↓
6. Payment Service processes mock payment
   ↓
7. Payment Service saves payment transaction
   ↓
8. Payment Service publishes payment.completed OR payment.failed event
   ↓
9. Order Service consumes payment event
   ↓
10. Order Service updates order status (CONFIRMED or PAYMENT_FAILED)
```

### Event Schema

**order.created**
```json
{
  "event_type": "order.created",
  "event_id": "uuid",
  "order_id": "uuid",
  "customer_id": "uuid",
  "amount": 100.00,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

**payment.completed/payment.failed**
```json
{
  "event_type": "payment.completed",
  "event_id": "uuid",
  "order_id": "uuid",
  "customer_id": "uuid",
  "amount": 100.00,
  "transaction_reference": "TXN-ABC123",
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Eventual Consistency

Due to the asynchronous nature of Kafka events, there is a brief period between order creation and payment processing where the order status remains PENDING_PAYMENT. This is expected behavior and provides eventual consistency.

## Installation

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)
- uv (Python package manager)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd Product-catalog-fastAPI-master
```

### 2. Install Dependencies (Local Development)

For each service, navigate to its directory and run:

```bash
cd services/auth-service
uv sync
```

Repeat for all services.

### 3. Configure Environment Variables

Copy the example environment file and customize:

```bash
cp .env.example .env
```

Edit `.env` with your preferred settings:

```env
POSTGRES_USER=ecommerce_user
POSTGRES_PASSWORD=ecommerce_password
AUTH_SECRET_KEY=your-super-secret-jwt-key-min-32-chars
AUTH_ADMIN_EMAIL=admin@ecommerce.com
AUTH_ADMIN_PASSWORD=admin123
PAYMENT_MOCK_SUCCESS_RATE=0.8
```

## Running the Application

### Using Docker Compose (Recommended)

1. Start all services:

```bash
docker compose up --build -d
```

2. Check service status:

```bash
docker compose ps
```

3. View logs:

```bash
docker compose logs -f
```

4. Stop services:

```bash
docker compose down
```

### Manual Setup (Development)

1. Start PostgreSQL and Kafka:

```bash
docker compose up postgres kafka kafka-ui -d
```

2. Run Alembic migrations for each service:

```bash
cd services/auth-service
uv run alembic upgrade head

cd ../product-service
uv run alembic upgrade head

cd ../order-service
uv run alembic upgrade head

cd ../payment-service
uv run alembic upgrade head
```

3. Run seed scripts:

```bash
cd services/auth-service
uv run python seed.py

cd ../product-service
uv run python seed.py
```

4. Start each service:

```bash
cd services/auth-service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# In separate terminals for other services
cd services/product-service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

cd services/order-service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

cd services/payment-service
uv run uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```

## API Documentation

Each service provides interactive API documentation via Swagger UI:

- **Auth Service**: http://localhost:8001/docs
- **Product Service**: http://localhost:8002/docs
- **Order Service**: http://localhost:8003/docs
- **Payment Service**: http://localhost:8004/docs

### Kafka UI

Monitor Kafka topics and messages at: http://localhost:8080

## Sample Workflows

### Admin Workflow

1. **Login as Admin**

```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@ecommerce.com",
    "password": "admin123"
  }'
```

2. **Create a Product**

```bash
curl -X POST http://localhost:8002/api/v1/products/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Laptop",
    "description": "High-performance laptop",
    "price": 999.99,
    "stock_quantity": 50
  }'
```

3. **View All Orders**

```bash
curl http://localhost:8003/api/v1/orders/
```

### Customer Workflow

1. **Register**

```bash
curl -X POST http://localhost:8001/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "password123",
    "full_name": "John Doe"
  }'
```

2. **Login**

```bash
curl -X POST http://localhost:8001/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "customer@example.com",
    "password": "password123"
  }'
```

Save the `access_token` from the response.

3. **Browse Products**

```bash
curl http://localhost:8002/api/v1/products/
```

4. **Add to Cart**

```bash
curl -X POST "http://localhost:8003/api/v1/cart/items?customer_id=<customer_uuid>" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": "<product_uuid>",
    "quantity": 2
  }'
```

5. **View Cart**

```bash
curl "http://localhost:8003/api/v1/cart/?customer_id=<customer_uuid>"
```

6. **Checkout**

```bash
curl -X POST "http://localhost:8003/api/v1/orders/checkout?customer_id=<customer_uuid>"
```

This will:
- Create an order with PENDING_PAYMENT status
- Publish an `order.created` event to Kafka
- Trigger payment processing asynchronously

7. **Check Order Status**

After a few seconds (for payment processing):

```bash
curl http://localhost:8003/api/v1/orders/<order_uuid>
```

The status should be either `CONFIRMED` or `PAYMENT_FAILED`.

8. **View Order History**

```bash
curl "http://localhost:8003/api/v1/orders/?customer_id=<customer_uuid>"
```

9. **Check Payment Status**

```bash
curl http://localhost:8004/api/v1/payments/order/<order_uuid>
```

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test Suite

```bash
pytest tests/integration/test_auth_service.py
pytest tests/integration/test_product_service.py
pytest tests/integration/test_order_service.py
pytest tests/integration/test_payment_service.py
```

### Run End-to-End Tests

```bash
pytest tests/e2e/
```

### Test Coverage

```bash
pytest --cov=services --cov-report=html
```

## Troubleshooting

### Services Won't Start

1. Check if ports are already in use:
```bash
netstat -an | grep 8001
```

2. Check Docker logs:
```bash
docker compose logs <service-name>
```

3. Verify environment variables are set correctly in `.env`

### Database Connection Issues

1. Ensure PostgreSQL is running:
```bash
docker compose ps postgres
```

2. Check database credentials in `.env`

3. Verify databases were created:
```bash
docker compose exec postgres psql -U ecommerce_user -d ecommerce -c "\l"
```

### Kafka Connection Issues

1. Check Kafka is running:
```bash
docker compose ps kafka
```

2. View Kafka logs:
```bash
docker compose logs kafka
```

3. Use Kafka UI to verify topics: http://localhost:8080

### Migration Issues

If migrations fail, you can reset a service's database:

```bash
docker compose exec postgres psql -U ecommerce_user -d ecommerce_auth -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
cd services/auth-service
uv run alembic upgrade head
```

### Payment Not Processing

1. Check Kafka topics are receiving events in Kafka UI
2. Verify Order Service is publishing `order.created` events
3. Check Payment Service logs for consumption errors
4. Ensure both services are connected to the same Kafka broker

### Alembic Commands

```bash
# Generate a new migration
cd services/<service-name>
uv run alembic revision --autogenerate -m "description"

# Apply migrations
uv run alembic upgrade head

# Rollback one migration
uv run alembic downgrade -1

# View migration history
uv run alembic history
```

## Development Notes

### Adding New Migrations

When modifying models:

1. Update the model file
2. Generate migration: `uv run alembic revision --autogenerate -m "description"`
3. Review the generated migration file
4. Apply migration: `uv run alembic upgrade head`

### Adding New Kafka Events

1. Define the topic in `infrastructure/kafka/topics.py`
2. Update producer/consumer in the relevant service
3. Add event schema documentation
4. Test the event flow

### Service Communication

- Use HTTP for synchronous calls (e.g., Order Service → Product Service)
- Use Kafka for asynchronous events (e.g., Order Service → Payment Service)
- Never access another service's database directly

## License

This project is provided as-is for educational purposes.

## Contributing

This is a demonstration project. For production use, consider:
- Adding comprehensive error handling
- Implementing retry logic for Kafka operations
- Adding distributed tracing
- Implementing circuit breakers
- Adding monitoring and alerting
- Implementing proper secret management
- Adding API rate limiting
- Implementing proper logging aggregation
