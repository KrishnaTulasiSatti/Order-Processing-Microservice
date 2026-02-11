from sqlalchemy.orm import Session
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

    # 4. Create outbox event (OrderProcessed – for now we mark processed directly)
    outbox_payload = {
        "orderId": event["orderId"],
        "status": "PROCESSED"
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