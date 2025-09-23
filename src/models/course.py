from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from src.database.database import Base


class Course(Base):
    """Course model for managing academic courses/grades"""

    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    academic_year = Column(String(9), nullable=False)  # e.g., "2024-2025"
    period = Column(Integer, nullable=False)  # 1, 2, 3 (trimestres)
    grade_level = Column(
        String(50), nullable=False
    )  # e.g., "Sexto", "Séptimo", "Octavo"
    name = Column(String(100), nullable=False)  # e.g., "Sexto A", "Séptimo B"
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    creator = relationship("User", back_populates="created_courses")
    students = relationship("CourseStudent", back_populates="course", lazy="dynamic")
    subjects = relationship("CourseSubject", back_populates="course", lazy="dynamic")
    classes = relationship("ClassModel", back_populates="course", lazy="dynamic")

    def __repr__(self):
        return f"<Course(id={self.id}, name='{self.name}', year='{self.academic_year}', period={self.period})>"
