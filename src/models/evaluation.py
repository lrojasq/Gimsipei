from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.database.database import Base


class Evaluation(Base):
    """Evaluation model for the application"""

    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    cover_image = Column(String(512), nullable=True)
    period = Column(Integer, nullable=False)  # 1, 2, 3, or 4
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationships
    course = relationship("Course", back_populates="evaluations")
    subject = relationship("Subject", back_populates="evaluations")
    creator = relationship("User", back_populates="created_evaluations")
    questions = relationship(
        "EvaluationQuestion",
        back_populates="evaluation",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    submissions = relationship(
        "EvaluationSubmission",
        back_populates="evaluation",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Evaluation(id={self.id}, title='{self.title}', period={self.period})>"
