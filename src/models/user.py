from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship

from src.database.database import Base


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
    avatar = Column(String(255), nullable=True)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    is_active = Column(Integer, default=1)

    # Relationships
    documents = relationship("Document", back_populates="author", lazy="dynamic")
    created_classes = relationship(
        "ClassModel", back_populates="creator", lazy="dynamic"
    )
    class_views = relationship("ClassView", back_populates="student", lazy="dynamic")
    created_books = relationship(
        "Book", back_populates="creator", foreign_keys="Book.created_by", lazy="dynamic"
    )

    # Course-related relationships
    created_courses = relationship("Course", back_populates="creator", lazy="dynamic")
    course_enrollments = relationship(
        "CourseStudent", back_populates="student", lazy="dynamic"
    )
    course_subject_assignments = relationship(
        "CourseSubject", back_populates="teacher", lazy="dynamic"
    )

    # Evaluation-related relationships
    created_evaluations = relationship(
        "Evaluation", back_populates="creator", lazy="dynamic"
    )
    evaluation_submissions = relationship(
        "EvaluationSubmission", back_populates="student", lazy="dynamic"
    )
