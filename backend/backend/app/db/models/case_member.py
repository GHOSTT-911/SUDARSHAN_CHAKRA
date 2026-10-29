from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.database import Base


class CaseMember(Base):
    __tablename__ = "CaseMembers"
    __table_args__ = (UniqueConstraint("case_id", "officer_id", name="uq_case_member"),)

    member_id = Column(String(50), primary_key=True)
    case_id = Column(String(50), ForeignKey("Cases.case_id"), nullable=False, index=True)
    officer_id = Column(String(50), ForeignKey("Officers.officer_id"), nullable=False, index=True)
    access_level = Column(String(30), nullable=False, default="viewer")
    assigned_at = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    case = relationship("Case", back_populates="members")
    officer = relationship("Officer", back_populates="case_memberships")
