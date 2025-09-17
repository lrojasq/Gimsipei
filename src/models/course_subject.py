from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from src.database.database import Base


class CourseSubject(Base):
    """Many-to-many relationship between courses and subjects"""

    __tablename__ = "course_subjects"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    course = relationship("Course", back_populates="subjects")
    subject = relationship("Subject", back_populates="course_assignments")
    teacher = relationship("User", back_populates="course_subject_assignments")

    def __repr__(self):
        return f"<CourseSubject(course_id={self.course_id}, subject_id={self.subject_id}, teacher_id={self.teacher_id})>"
