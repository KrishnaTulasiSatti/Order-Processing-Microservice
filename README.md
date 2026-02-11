# Order Processing Microservice

A robust, production-ready microservice built with **FastAPI**, **SQLAlchemy**, and **RabbitMQ**. This service implements the **Transactional Outbox Pattern** to ensure reliable event delivery and handles order processing with strict **idempotency**.

## 🚀 Features

- **FastAPI Core**: High-performance asynchronous API framework.
- **Transactional Outbox Pattern**: Ensures "at-least-once" message delivery by saving events in the same database transaction as business logic.
- **Idempotent Processing**: Prevents duplicate order processing using an `idempotencyKey`.
- **Infrastructure Resilience**:
  - Automatic database connection retries on startup.
  - Heartbeat-aware RabbitMQ connection management.
  - Background worker auto-reconnection logic.
- **Health Monitoring**: `/health` endpoint providing real-time status of DB and MQ connections.
- **Dockerized**: Fully containerized environment with health checks and volume persistence.

## 🏗️ Architecture

1.  **Order Consumer**: Listens for `OrderCreated` events from RabbitMQ.
2.  **Service Layer**: Validates orders, checks for duplicates, and updates the database.
3.  **Outbox Table**: High-consistency buffer for outgoing events.
4.  **Outbox Publisher**: A dedicated background worker that polls the outbox table and publishes events to RabbitMQ.

---

## 🛠️ Getting Started

### Prerequisites

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Running the Project

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/KrishnaTulasiSatti/Order-Processing-Microservice.git
    cd Order-Processing-Microservice
    ```

2.  **Start with Docker Compose**:
    ```bash
    docker-compose up --build
    ```

3.  **Verify Health**:
    Access the health check endpoint at [http://localhost:8000/health](http://localhost:8000/health).

---

## ⚙️ Environment Configuration

Configuration is managed via environment variables. Refer to `.env.example` for a complete list.

| Variable | Description | Default |
| :--- | :--- | :--- |
| `DB_HOST` | MySQL database host | `db` |
| `MQ_HOST` | RabbitMQ host | `rabbitmq` |
| `INCOMING_ORDER_QUEUE` | Queue for incoming orders | `order_created_queue` |
| `OUTGOING_PROCESSED_QUEUE` | Queue for processed order events | `order_processed_queue` |

---

## 📂 Project Structure

```text
├── src/
│   ├── config/         # Database, RabbitMQ, and App settings
│   ├── consumers/      # RabbitMQ message consumers
│   ├── models/         # SQLAlchemy ORM models
│   ├── repositories/   # Data access layer
│   ├── services/       # Business logic
│   ├── workers/        # Background publishers/pollers
│   └── main.py         # FastAPI entry point
├── db_init/            # SQL scripts for database initialization
├── Dockerfile          # App container definition
└── docker-compose.yml  # Orchestration of all services
```

---

## 🧪 Testing

To simulate an order, publish a message to the `order_created_queue` in the [RabbitMQ Management UI](http://localhost:15672) (default login: `guest`/`guest`):

**Example Payload:**
```json
{
  "orderId": "order-101",
  "userId": "user-456",
  "totalAmount": 99.99,
  "idempotencyKey": "unique-key-001",
  "items": []
}
```

---

## 🛡️ Stability & Reliability

This microservice has been hardened with:
- **Lifespan Management**: Clean startup and shutdown of background threads.
- **DB Wait Utility**: The app waits for the database to be "Ready" (healthy) before starting workers.
- **Schema Validation**: Automated SQL schema synchronization with Python models.
