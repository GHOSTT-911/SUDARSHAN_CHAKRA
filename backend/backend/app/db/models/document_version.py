from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.database import Base


class DocumentVersion(Base):
    __tablename__ = "DocumentVersions"
    __table_args__ = (UniqueConstraint("document_id", "version_number", name="uq_document_version"),)

    version_id = Column(String(50), primary_key=True)
    document_id = Column(String(50), ForeignKey("Documents.document_id"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    storage_path = Column(String(500), nullable=False)
    sha256_hash = Column(String(64), nullable=False)
    original_filename = Column(String(255), nullable=False)
    uploaded_by = Column(String(50), ForeignKey("Officers.officer_id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    document = relationship("Document", back_populates="versions")
    uploader = relationship("Officer")
