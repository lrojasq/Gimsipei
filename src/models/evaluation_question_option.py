from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from src.database.database import Base


class EvaluationQuestionOption(Base):
    """Evaluation Question Option model - Stores options for multiple choice questions"""

    __tablename__ = "evaluation_question_options"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("evaluation_questions.id"), nullable=False)
    option_letter = Column(String(1), nullable=False)  # A, B, C, D, etc.
    option_text = Column(String(500), nullable=False)
    display_order = Column(Integer, nullable=False)  # Order in which options appear

    # Relationships
    question = relationship("EvaluationQuestion", back_populates="options")

    def __repr__(self):
        return f"<EvaluationQuestionOption(id={self.id}, letter={self.option_letter}, text='{self.option_text[:30]}...')>"
