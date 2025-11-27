from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from src.database.database import Base
from datetime import datetime, timezone


class Assignment(Base):
    """Assignment model for tasks assigned to students within a class"""

    __tablename__ = "assignments"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(
        Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False
    )
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    max_score = Column(Integer, nullable=True, default=100)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationships
    class_ = relationship("ClassModel", back_populates="assignments")
    creator = relationship("User", foreign_keys=[created_by])
    submissions = relationship(
        "AssignmentSubmission", back_populates="assignment", lazy="dynamic"
    )
