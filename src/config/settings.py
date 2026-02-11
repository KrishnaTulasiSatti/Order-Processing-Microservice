import os

DB_USER = os.getenv("DB_USER", "user")
DB_PASS = os.getenv("DB_PASSWORD", "password")
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "order_db")

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

RABBITMQ_HOST = os.getenv("MQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("MQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("MQ_USER", "guest")
RABBITMQ_PASS = os.getenv("MQ_PASSWORD", "guest")
RABBITMQ_QUEUE = os.getenv("INCOMING_ORDER_QUEUE", "order_created_queue")
OUTGOING_PROCESSED_QUEUE = os.getenv("OUTGOING_PROCESSED_QUEUE", "order_processed_queue")
OUTGOING_FAILED_QUEUE = os.getenv("OUTGOING_FAILED_QUEUE", "order_failed_queue")