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

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    document = Column(String(20), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Integer, default=1)

    # Relationships
    documents = relationship("Document", back_populates="author", lazy="dynamic")
    exercises = relationship("Exercise", back_populates="author", lazy="dynamic")
    assignments = relationship("Assignment", back_populates="author", lazy="dynamic")
    submissions = relationship("Submission", back_populates="student", lazy="dynamic")
    subjects = relationship("Subject", back_populates="teacher", lazy="dynamic")
    created_classes = relationship(
        "ClassModel", back_populates="creator", lazy="dynamic"
    )
    class_views = relationship("ClassView", back_populates="student", lazy="dynamic")

    # New course-related relationships
    created_courses = relationship("Course", back_populates="creator", lazy="dynamic")
    course_enrollments = relationship(
        "CourseStudent", back_populates="student", lazy="dynamic"
    )
    course_subject_assignments = relationship(
        "CourseSubject", back_populates="teacher", lazy="dynamic"
    )
