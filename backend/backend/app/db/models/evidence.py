from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class Evidence(Base):
    __tablename__ = "Evidence"

    evidence_id = Column(String(50), primary_key=True)

    case_id = Column(
        String(50),
        ForeignKey("Cases.case_id"),
        nullable=False
    )

    sha256_hash = Column(String(64), nullable=False)

    encrypted_storage_path = Column(
        String(255),
        nullable=False
    )

    uploaded_by = Column(
        String(50),
        ForeignKey("Officers.officer_id"),
        nullable=False
    )

    upload_timestamp = Column(
        DateTime,
        nullable=True
    )

    case = relationship("Case")
    uploader = relationship("Officer")