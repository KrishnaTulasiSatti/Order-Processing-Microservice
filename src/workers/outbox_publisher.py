import time
import json
import pika
from config.rabbitmq import get_rabbitmq_connection
from config.database import SessionLocal
from repositories.outbox_repository import get_pending_outbox_events, mark_outbox_event_sent

from config.settings import OUTGOING_PROCESSED_QUEUE

def start_outbox_publisher():
    print("📤 Starting Outbox Publisher...", flush=True)

    while True:
        try:
            connection = get_rabbitmq_connection()
            channel = connection.channel()
            channel.queue_declare(queue=OUTGOING_PROCESSED_QUEUE, durable=True)

            while True:
                db = SessionLocal()
                try:
                    events = get_pending_outbox_events(db)

                    for event in events:
                        channel.basic_publish(
                            exchange="",
                            routing_key=OUTGOING_PROCESSED_QUEUE,
                            body=json.dumps(event.payload).encode(),
                            properties=pika.BasicProperties(delivery_mode=2),
                        )
                        print(f"📤 Published outbox event: {event.id}", flush=True)
                        event.status = "SENT"  # ✅ Direct update is more efficient
                    
                    db.commit()  # ✅ MISSING COMMIT FIXED
                except Exception as e:
                    db.rollback()
                    print(f"❌ Error in outbox batch: {e}", flush=True)
                finally:
                    db.close()
                
                time.sleep(5)

        except Exception as e:
            print(f"❌ Outbox publisher connection error: {e}", flush=True)
            time.sleep(5)