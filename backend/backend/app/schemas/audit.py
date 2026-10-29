from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AuditEventResponse(BaseModel):
    event_id: str
    actor_id: str | None
    action: str
    target_type: str
    target_id: str | None
    case_id: str | None
    timestamp: datetime
    ip_address: str | None
    details: str | None
    previous_hash: str | None
    event_hash: str

    model_config = ConfigDict(from_attributes=True)
