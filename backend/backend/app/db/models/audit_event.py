from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, Text

from app.db.database import Base


class AuditEvent(Base):
    __tablename__ = "AuditEvents"

    event_id = Column(String(50), primary_key=True)
    actor_id = Column(String(50), ForeignKey("Officers.officer_id"), nullable=True, index=True)
    action = Column(String(80), nullable=False, index=True)
    target_type = Column(String(50), nullable=False)
    target_id = Column(String(50), nullable=True, index=True)
    case_id = Column(String(50), nullable=True, index=True)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)
    ip_address = Column(String(45), nullable=True)
    details = Column(Text, nullable=True)
    previous_hash = Column(String(64), nullable=True)
    event_hash = Column(String(64), nullable=False, unique=True)
