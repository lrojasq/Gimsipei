from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from src.database.database import Base

class Exercise(Base):
    """Exercise model for storing quizzes and tests"""
    __tablename__ = "exercises"

    id: int = Column(Integer, primary_key=True, index=True)
    title: str = Column(String(255), nullable=False)
    description: str = Column(Text, nullable=False)
    questions: dict = Column(JSON, nullable=False)  # Store questions and answers in JSON format
    author_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    time_limit: int = Column(Integer, nullable=True)  # Time limit in minutes
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: bool = Column(Integer, default=1)

    # Relationships
    author = relationship("User", back_populates="exercises")
    submissions = relationship("Submission", back_populates="exercise")
