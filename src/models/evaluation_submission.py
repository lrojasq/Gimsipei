from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.database.database import Base


class EvaluationSubmission(Base):
    """Evaluation Submission model - Stores student submissions for evaluations"""

    __tablename__ = "evaluation_submissions"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    score = Column(Float, nullable=True)  # Calculated score
    total_questions = Column(Integer, nullable=False, default=10)
    correct_answers = Column(Integer, nullable=True)
    is_completed = Column(Boolean, default=False)
    submitted_at = Column(DateTime, default=datetime.now(timezone.utc))
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationships
    evaluation = relationship("Evaluation", back_populates="submissions")
    student = relationship("User", back_populates="evaluation_submissions")
    answers = relationship(
        "EvaluationSubmissionAnswer",
        back_populates="submission",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<EvaluationSubmission(id={self.id}, evaluation_id={self.evaluation_id}, student_id={self.student_id}, score={self.score})>"
