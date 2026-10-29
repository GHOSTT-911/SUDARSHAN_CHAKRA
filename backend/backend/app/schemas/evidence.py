from datetime import datetime

from pydantic import BaseModel, ConfigDict


class EvidenceResponse(BaseModel):
    evidence_id: str
    case_id: str
    sha256_hash: str
    encrypted_storage_path: str
    uploaded_by: str
    upload_timestamp: datetime | None = None

    model_config = ConfigDict(from_attributes=True)