from sqlalchemy import Column, String, DECIMAL, TIMESTAMP, func
from config.database import Base

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String(255), primary_key=True, index=True)
    user_id = Column(String(255), nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(50), nullable=False)
    idempotency_key = Column(String(255), unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())