from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database.database import Base
from datetime import datetime, timezone


class ClassContent(Base):
    """ClassContent model for storing educational content within a class"""

    __tablename__ = "class_contents"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(
        Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False
    )
    content_order = Column(Integer, nullable=False, default=1)
    section_title = Column(String(200), nullable=True)  # e.g., "Cómo funciona:"
    content_text = Column(Text, nullable=True)  # Main text content
    content_image = Column(String(255), nullable=True)  # Image URL if any
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationships
    class_ = relationship("ClassModel", back_populates="contents")
