import json
import os
from config.rabbitmq import get_rabbitmq_connection
from config.database import SessionLocal
from services.order_service import process_order_created_event

QUEUE_NAME = os.getenv("INCOMING_ORDER_QUEUE", "order_created_queue")

import time

def start_order_consumer():
    print("🚀 Starting Order Consumer...", flush=True)

    while True:
        try:
            connection = get_rabbitmq_connection()
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)

            def callback(ch, method, properties, body):
                db = SessionLocal()
                try:
                    event = json.loads(body.decode())
                    print("📩 Received OrderCreated event:", event, flush=True)

                    process_order_created_event(db, event)
                    db.commit()  # 🔒 Transaction commit

                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    print("✅ Order processed and committed", flush=True)

                except Exception as e:
                    db.rollback()
                    print("❌ Error processing order:", str(e), flush=True)
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

                finally:
                    db.close()

            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback)

            print("🐇 Waiting for OrderCreated events...", flush=True)
            channel.start_consuming()

        except Exception as e:
            print(f"❌ Order consumer connection error: {e}. Retrying in 5s...", flush=True)
            time.sleep(5)