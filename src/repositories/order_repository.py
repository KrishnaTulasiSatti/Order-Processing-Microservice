from sqlalchemy.orm import Session
from models.order import Order

def get_order_by_idempotency_key(db: Session, key: str):
    return db.query(Order).filter(Order.idempotency_key == key).first()

def create_order(db: Session, order_id, user_id, total_amount, status, idempotency_key):
    order = Order(
        order_id=order_id,
        user_id=user_id,
        total_amount=total_amount,
        status=status,
        idempotency_key=idempotency_key
    )
    db.add(order)
    return order

def update_order_status(db: Session, order_id: str, status: str):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if order:
        order.status = status
    return order