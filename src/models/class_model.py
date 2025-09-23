from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database.database import Base
from datetime import datetime, timezone


class ClassModel(Base):
    """Class model for the application"""

    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    period_id = Column(Integer, ForeignKey("periods.id"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    class_number = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc)
    )

    # Relationships
    period = relationship("Period", back_populates="classes")
    creator = relationship("User", back_populates="created_classes")
    resources = relationship("Resource", back_populates="class_", lazy="dynamic")
    assignments = relationship("Assignment", back_populates="class_", lazy="dynamic")
    views = relationship("ClassView", back_populates="class_", lazy="dynamic")
