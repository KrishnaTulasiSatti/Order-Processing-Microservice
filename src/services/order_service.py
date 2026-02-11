from sqlalchemy.orm import Session
from datetime import datetime
from repositories.order_repository import (
    get_order_by_idempotency_key,
    create_order,
    update_order_status
)
from repositories.outbox_repository import create_outbox_event

def process_order_created_event(db: Session, event: dict):
    # 1. Basic validation
    required_fields = ["orderId", "userId", "items", "totalAmount", "idempotencyKey"]
    for field in required_fields:
        if field not in event:
            raise ValueError(f"Missing field: {field}")

    if event["totalAmount"] <= 0:
        raise ValueError("Total amount must be positive")

    # 2. Idempotency check
    existing = get_order_by_idempotency_key(db, event["idempotencyKey"])
    if existing:
        print("🔁 Duplicate event detected, skipping processing")
        return existing

    # 3. Create order (PENDING)
    order = create_order(
        db=db,
        order_id=event["orderId"],
        user_id=event["userId"],
        total_amount=event["totalAmount"],
        status="PENDING",
        idempotency_key=event["idempotencyKey"]
    )

    # 4. Create outbox event (OrderProcessed)
    outbox_payload = {
        "orderId": event["orderId"],
        "status": "PROCESSED",
        "processingTimestamp": datetime.utcnow().isoformat() + "Z"
    }

    create_outbox_event(
        db=db,
        event_type="OrderProcessed",
        aggregate_type="Order",
        aggregate_id=event["orderId"],
        payload=outbox_payload
    )

    # 5. Update order status
    update_order_status(db, event["orderId"], "PROCESSED")

    return order

def handle_order_failure(db: Session, order_id: str, reason: str, error_details: str):
    """Creates an OrderFailed event in the outbox."""
    outbox_payload = {
        "orderId": order_id,
        "reason": reason,
        "errorDetails": error_details
    }

    create_outbox_event(
        db=db,
        event_type="OrderFailed",
        aggregate_type="Order",
        aggregate_id=order_id,
        payload=outbox_payload
    )
    
    # Also update order status if order_id exists
    if order_id:
        update_order_status(db, order_id, "FAILED")