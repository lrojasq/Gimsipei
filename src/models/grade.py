from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from src.database.database import Base
from datetime import datetime, timezone


class Grade(Base):
    """Grade model for storing student grades per subject and period"""

    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    period = Column(Integer, nullable=False)  # 1, 2, 3, or 4

    # Grade components
    tasks_grade = Column(Float, nullable=True)  # Tareas
    assignments_grade = Column(Float, nullable=True)  # Trabajos
    evaluations_grade = Column(Float, nullable=True)  # Evaluaciones
    final_grade = Column(Float, nullable=True)  # Nota final del periodo

    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationships
    student = relationship("User", foreign_keys=[student_id])
    course = relationship("Course")
    subject = relationship("Subject")

    # Ensure unique grade per student, course, subject, and period
    __table_args__ = (
        UniqueConstraint(
            "student_id",
            "course_id",
            "subject_id",
            "period",
            name="unique_student_grade_per_period",
        ),
    )

    def __repr__(self):
        return f"<Grade(id={self.id}, student_id={self.student_id}, subject_id={self.subject_id}, period={self.period}, final_grade={self.final_grade})>"
