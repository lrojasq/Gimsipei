from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database.database import Base
from datetime import datetime, timezone


class ClassModel(Base):
    """Class model for the application"""

    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    class_number = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationships
    course = relationship("Course", back_populates="classes")
    subject = relationship("Subject")
    creator = relationship("User", back_populates="created_classes")
    resources = relationship("Resource", back_populates="class_", lazy="dynamic")
    assignments = relationship("Assignment", back_populates="class_", lazy="dynamic")
    views = relationship("ClassView", back_populates="class_", lazy="dynamic")
