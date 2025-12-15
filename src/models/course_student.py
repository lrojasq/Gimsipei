from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.database.database import Base


class CourseStudent(Base):
    """Many-to-many relationship between courses and students"""

    __tablename__ = "course_students"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationships
    course = relationship("Course", back_populates="students")
    student = relationship("User", back_populates="course_enrollments")

    def __repr__(self):
        return (
            f"<CourseStudent(course_id={self.course_id}, student_id={self.student_id})>"
        )
