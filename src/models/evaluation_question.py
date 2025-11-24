from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from src.database.database import Base
from datetime import datetime, timezone


class QuestionType:
    """Question type constants"""

    OPEN = "open"  # Respuesta abierta
    MULTIPLE_CHOICE = "multi"  # Opción múltiple


class EvaluationQuestion(Base):
    """Evaluation Question model - Stores questions for evaluations"""

    __tablename__ = "evaluation_questions"

    id = Column(Integer, primary_key=True, index=True)
    evaluation_id = Column(Integer, ForeignKey("evaluations.id"), nullable=False)
    question_number = Column(Integer, nullable=False)  # 1-10
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), nullable=False)
    correct_answer = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationships
    evaluation = relationship("Evaluation", back_populates="questions")
    options = relationship(
        "EvaluationQuestionOption",
        back_populates="question",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<EvaluationQuestion(id={self.id}, question_number={self.question_number}, type={self.question_type})>"
