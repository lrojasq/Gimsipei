from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from src.database.database import Base


class ClassView(Base):
    """ClassView model for the application"""

    __tablename__ = "class_views"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    viewed_at = Column(DateTime, default=datetime.now(timezone.utc))

    # Relationships
    class_ = relationship("ClassModel", back_populates="views")
    student = relationship("User", back_populates="class_views")
