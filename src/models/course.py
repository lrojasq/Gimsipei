from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from src.database.database import Base


class Course(Base):
    """Course model for managing academic courses/grades"""

    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    academic_year = Column(String(4), nullable=False)
    name = Column(String(100), nullable=False)  # e.g., "Sexto"...
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationships
    creator = relationship("User", back_populates="created_courses")
    students = relationship(
        "CourseStudent",
        back_populates="course",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    subjects = relationship(
        "CourseSubject",
        back_populates="course",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    classes = relationship(
        "ClassModel",
        back_populates="course",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    evaluations = relationship(
        "Evaluation",
        back_populates="course",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )
    grades = relationship("Grade", back_populates="course", lazy="dynamic")

    def __repr__(self):
        return (
            f"<Course(id={self.id}, name='{self.name}', year='{self.academic_year}')>"
        )
