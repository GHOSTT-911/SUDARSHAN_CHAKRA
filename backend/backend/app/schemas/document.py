from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    document_id: str
    case_id: str
    title: str
    document_type: str
    original_filename: str
    sha256_hash: str
    encrypted: bool
    uploaded_by: str
    current_version: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentVersionResponse(BaseModel):
    version_id: str
    document_id: str
    version_number: int
    sha256_hash: str
    original_filename: str
    uploaded_by: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
