from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Float
from sqlalchemy.orm import relationship
from src.database.database import Base


class Submission(Base):
    """Submission model for exercise and assignment submissions"""

    __tablename__ = "submissions"

    id: int = Column(Integer, primary_key=True, index=True)
    student_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    exercise_id: int = Column(Integer, ForeignKey("exercises.id"), nullable=True)
    assignment_id: int = Column(Integer, ForeignKey("assignments.id"), nullable=True)
    content: dict = Column(
        JSON, nullable=False
    )  # Store submission content in JSON format
    score: float = Column(Float, nullable=True)
    feedback: str = Column(Text, nullable=True)
    submitted_at: datetime = Column(DateTime, default=datetime.utcnow)
    is_active: bool = Column(Integer, default=1)

    # Relationships
    student = relationship("User", back_populates="submissions")
    exercise = relationship("Exercise", back_populates="submissions")
    assignment = relationship("Assignment", back_populates="submissions")
