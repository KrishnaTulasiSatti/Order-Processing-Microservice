import json
import os
from config.rabbitmq import get_rabbitmq_connection
from config.database import SessionLocal

QUEUE_NAME = os.getenv("INCOMING_ORDER_QUEUE", "order_created_queue")

import time

from services.order_service import process_order_created_event, handle_order_failure

def start_order_consumer():
    print("🚀 Starting Order Consumer...", flush=True)

    while True:
        try:
            connection = get_rabbitmq_connection()
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)

            def callback(ch, method, properties, body):
                db = SessionLocal()
                event_data = {}
                try:
                    event_data = json.loads(body.decode())
                    print(f"📩 Received OrderCreated event: {event_data}", flush=True)

                    process_order_created_event(db, event_data)
                    db.commit()

                    ch.basic_ack(delivery_tag=method.delivery_tag)
                    print("✅ Order processed and committed", flush=True)

                except Exception as e:
                    db.rollback()
                    print(f"❌ Error processing order: {str(e)}", flush=True)
                    
                    # Record failure in outbox
                    try:
                        order_id = event_data.get("orderId", "UNKNOWN")
                        handle_order_failure(
                            db, 
                            order_id, 
                            reason="PROCESSING_ERROR", 
                            error_details=str(e)
                        )
                        db.commit()
                        print(f"📉 Order failure recorded for {order_id}", flush=True)
                    except Exception as failure_err:
                        print(f"🚨 Failed to record order failure: {failure_err}", flush=True)

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