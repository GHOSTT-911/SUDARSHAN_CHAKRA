from sqlalchemy import Column, Date, Enum, ForeignKey, String
from sqlalchemy.orm import relationship

from app.db.database import Base


class Case(Base):
    __tablename__ = "Cases"

    case_id = Column(String(50), primary_key=True)
    crime_domain = Column(String(100), nullable=False)
    filing_date = Column(Date, nullable=False)
    status = Column(
        Enum(
            "Pending Review",
            "Verified & Sealed",
            "Closed"
        ),
        nullable=False
    )

    assigned_judge_id = Column(
        String(50),
        ForeignKey("Officers.officer_id")
    )

    assigned_judge = relationship("Officer")
    members = relationship("CaseMember", back_populates="case", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="case", cascade="all, delete-orphan")
