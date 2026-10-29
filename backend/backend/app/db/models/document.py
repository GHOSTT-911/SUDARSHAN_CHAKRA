from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.database import Base


class Document(Base):
    __tablename__ = "Documents"

    document_id = Column(String(50), primary_key=True)
    case_id = Column(String(50), ForeignKey("Cases.case_id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    document_type = Column(String(50), nullable=False, default="Other")
    original_filename = Column(String(255), nullable=False)
    storage_path = Column(String(500), nullable=False)
    sha256_hash = Column(String(64), nullable=False)
    encrypted = Column(Boolean, nullable=False, default=True)
    uploaded_by = Column(String(50), ForeignKey("Officers.officer_id"), nullable=False)
    current_version = Column(Integer, nullable=False, default=1)
    extracted_text = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    case = relationship("Case", back_populates="documents")
    uploader = relationship("Officer")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
