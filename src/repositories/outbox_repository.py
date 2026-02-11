from sqlalchemy.orm import Session
from models.outbox import OutboxEvent

def create_outbox_event(
    db: Session,
    event_type: str,
    aggregate_type: str,
    aggregate_id: str,
    payload: dict
):
    event = OutboxEvent(
        event_type=event_type,
        aggregate_type=aggregate_type,
        aggregate_id=aggregate_id,
        payload=payload,
        status="PENDING"
    )
    db.add(event)
    db.flush()  # so event.id is available before commit
    return event

def get_pending_outbox_events(db: Session, limit: int = 10):
    return (
        db.query(OutboxEvent)
        .filter(OutboxEvent.status == "PENDING")
        .order_by(OutboxEvent.created_at.asc())
        .limit(limit)
        .all()
    )

def mark_outbox_event_sent(db: Session, event_id: int):
    event = db.query(OutboxEvent).filter(OutboxEvent.id == event_id).first()
    if event:
        event.status = "SENT"