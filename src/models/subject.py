from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from src.database.database import Base


class Subject(Base):
    """Subject model for the application"""

    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    image_url = Column(String(255), nullable=True)

    # Relationships
    course_assignments = relationship(
        "CourseSubject", back_populates="subject", lazy="dynamic"
    )
    classes = relationship("ClassModel", back_populates="subject", lazy="dynamic")
    evaluations = relationship("Evaluation", back_populates="subject", lazy="dynamic")
    grades = relationship("Grade", back_populates="subject", lazy="dynamic")
