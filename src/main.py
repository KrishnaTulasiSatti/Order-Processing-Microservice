from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
import threading

from config.database import get_db

print("✅ main.py loaded", flush=True)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("⚙️ FastAPI startup: Waiting for services...", flush=True)
    from config.db_wait import wait_for_db
    wait_for_db()  # ✅ Ensure DB is ready before starting workers

    from consumers.order_consumer import start_order_consumer
    from workers.outbox_publisher import start_outbox_publisher

    threading.Thread(target=start_order_consumer, daemon=True).start()
    threading.Thread(target=start_outbox_publisher, daemon=True).start()
    yield
    print("⚙️ FastAPI shutdown: Background threads will stop...", flush=True)

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def health(db: Session = Depends(get_db)):
    return {
        "status": "OK",
        "db": "connected",
        "mq": "connected"
    }