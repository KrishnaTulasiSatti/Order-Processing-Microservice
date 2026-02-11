import pika
import os
import time

from config.settings import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PASS

def get_rabbitmq_connection(retries=10, delay=5):
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)

    parameters = pika.ConnectionParameters(
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        credentials=credentials,
        heartbeat=60
    )

    for attempt in range(1, retries + 1):
        try:
            print(f"🔌 Connecting to RabbitMQ (attempt {attempt}/{retries})...")
            return pika.BlockingConnection(parameters)
        except pika.exceptions.AMQPConnectionError:
            print(f"❌ RabbitMQ not ready. Retrying in {delay} seconds...")
            time.sleep(delay)

    raise Exception("❌ Could not connect to RabbitMQ after multiple retries")