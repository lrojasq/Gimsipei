from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from src.database.database import Base
from datetime import datetime, timezone


class AssignmentSubmission(Base):
    """AssignmentSubmission model for student task submissions"""

    __tablename__ = "assignment_submissions"

    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(
        Integer, ForeignKey("assignments.id", ondelete="CASCADE"), nullable=False
    )
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    submission_text = Column(Text, nullable=True)
    file_url = Column(String(255), nullable=True)  # URL to uploaded file
    score = Column(Float, nullable=True)  # Grade given by teacher
    feedback = Column(Text, nullable=True)  # Teacher's feedback
    submitted_at = Column(DateTime, default=datetime.now(timezone.utc))
    graded_at = Column(DateTime, nullable=True)

    # Relationships
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", foreign_keys=[student_id])
