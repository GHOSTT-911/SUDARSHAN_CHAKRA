import hashlib
import json
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy.orm import Session

from app.db.models import AuditEvent, Officer


def log_event(db: Session, actor: Officer | None, action: str, target_type: str,
              target_id: str | None = None, case_id: str | None = None,
              ip_address: str | None = None, details: dict | None = None) -> AuditEvent:
    previous = db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).first()
    previous_hash = previous.event_hash if previous else None
    timestamp = datetime.now(timezone.utc)
    body = json.dumps({"actor_id": actor.officer_id if actor else None, "action": action,
                       "target_type": target_type, "target_id": target_id, "case_id": case_id,
                       "timestamp": timestamp.isoformat(), "details": details or {}, "previous_hash": previous_hash}, sort_keys=True)
    event = AuditEvent(event_id=f"AUD-{uuid4().hex[:20]}", actor_id=actor.officer_id if actor else None,
                       action=action, target_type=target_type, target_id=target_id, case_id=case_id,
                       timestamp=timestamp, ip_address=ip_address, details=json.dumps(details or {}),
                       previous_hash=previous_hash, event_hash=hashlib.sha256(body.encode()).hexdigest())
    db.add(event)
    return event
