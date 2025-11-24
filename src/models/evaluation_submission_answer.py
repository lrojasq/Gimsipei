from sqlalchemy import Column, Integer, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from src.database.database import Base


class EvaluationSubmissionAnswer(Base):
    """Evaluation Submission Answer model - Stores individual answers for each question"""

    __tablename__ = "evaluation_submission_answers"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(
        Integer, ForeignKey("evaluation_submissions.id"), nullable=False
    )
    question_id = Column(Integer, ForeignKey("evaluation_questions.id"), nullable=False)
    answer_text = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=False, default=False)
    points_earned = Column(Integer, nullable=True, default=0)

    # Relationships
    submission = relationship("EvaluationSubmission", back_populates="answers")
    question = relationship("EvaluationQuestion")

    def __repr__(self):
        return f"<EvaluationSubmissionAnswer(id={self.id}, question_id={self.question_id}, is_correct={self.is_correct})>"
