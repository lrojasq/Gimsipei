from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from src.database.database import Base
from enum import Enum as PyEnum

class UserRole(PyEnum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

class User(Base):
    """User model for the application"""
    __tablename__ = "users"

    id: int = Column(Integer, primary_key=True, index=True)
    email: str = Column(String(255), unique=True, index=True, nullable=False)
    username: str = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password: str = Column(String(255), nullable=False)
    full_name: str = Column(String(100), nullable=True)
    role: UserRole = Column(Enum(UserRole), nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active: bool = Column(Integer, default=1)

    # Relationships
    documents = relationship("Document", back_populates="author")
    exercises = relationship("Exercise", back_populates="author")
    assignments = relationship("Assignment", back_populates="author")
    submissions = relationship("Submission", back_populates="student")
