from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.database.database import Base


class Document(Base):
    """Document model for storing educational materials"""

    __tablename__ = "documents"

    id: int = Column(Integer, primary_key=True, index=True)
    title: str = Column(String(255), nullable=False)
    content: str = Column(Text, nullable=False)
    author_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at: datetime = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )
    is_active: bool = Column(Integer, default=1)

    # Relationships
    author = relationship("User", back_populates="documents")
