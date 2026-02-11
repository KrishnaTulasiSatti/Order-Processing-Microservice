from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from config.database import Base

class OutboxEvent(Base):
    __tablename__ = "outbox"

    id = Column(Integer, primary_key=True, index=True)
    aggregate_type = Column(String(255), nullable=False)
    aggregate_id = Column(String(255), nullable=False)
    event_type = Column(String(255), nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False, default="PENDING")
    created_at = Column(DateTime(timezone=True), server_default=func.now())