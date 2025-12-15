from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.database.database import Base


class Book(Base):
    """Book model for storing educational books"""

    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    description = Column(Text, default="")
    file_path = Column(String(512), nullable=False)
    cover_image = Column(String(512), nullable=True)
    target_audience = Column(String(20), nullable=False)
    grade_level = Column(Integer, nullable=True)  # Grado: 6, 7, 8, 9, 10, 11
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )

    # Relationships
    creator = relationship(
        "User", back_populates="created_books", foreign_keys=[created_by]
    )
