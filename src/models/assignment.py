from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.database.database import Base

class Assignment(Base):
    """Assignment model for homework and tasks"""
    __tablename__ = "assignments"

    id: int = Column(Integer, primary_key=True, index=True)
    title: str = Column(String(255), nullable=False)
    description: str = Column(Text, nullable=False)
    author_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    due_date: datetime = Column(DateTime, nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: bool = Column(Integer, default=1)

    # Relationships
    author = relationship("User", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")
