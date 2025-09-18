from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database.database import Base
from datetime import datetime, timezone


class Subject(Base):
    """Subject model for the application"""

    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationships
    teacher = relationship("User", back_populates="subjects")
    periods = relationship("Period", back_populates="subject", lazy="dynamic")
    course_assignments = relationship(
        "CourseSubject", back_populates="subject", lazy="dynamic"
    )
