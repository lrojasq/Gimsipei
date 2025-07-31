from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.database.database import Base

class Assignment(Base):
    """Assignment model for the application"""

    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    due_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    class_ = relationship("ClassModel", back_populates="assignments")
    author = relationship("User", back_populates="assignments")
    submissions = relationship(
        "Submission", back_populates="assignment", lazy="dynamic"
    )
