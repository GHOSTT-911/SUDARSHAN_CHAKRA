from sqlalchemy import Boolean, Column, Enum, String, Text
from sqlalchemy.orm import relationship
from app.db.database import Base


class Officer(Base):
    __tablename__ = "Officers"

    officer_id = Column(String(50), primary_key=True)
    full_name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    role_clearance = Column(
        Enum("police", "judge", "admin"),
        nullable=False
    )
    password_hash = Column(String(255), nullable=False)
    public_key = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)

    case_memberships = relationship("CaseMember", back_populates="officer")
