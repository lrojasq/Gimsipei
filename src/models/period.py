from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database.database import Base
from datetime import datetime


class Period(Base):
    """Period model for the application"""

    __tablename__ = "periods"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    is_locked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    # Relationships
    subject = relationship("Subject", back_populates="periods")
