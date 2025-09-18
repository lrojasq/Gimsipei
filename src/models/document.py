from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from src.database.database import Base


class Document(Base):
    """Document model for storing educational materials"""

    __tablename__ = "documents"

    id: int = Column(Integer, primary_key=True, index=True)
    title: str = Column(String(255), nullable=False)
    content: str = Column(Text, nullable=False)
    author_id: int = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_active: bool = Column(Integer, default=1)

    # Relationships
    author = relationship("User", back_populates="documents")
