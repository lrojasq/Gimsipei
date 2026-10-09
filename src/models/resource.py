from datetime import UTC, datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database.database import Base


class ResourceType(PyEnum):
    FILE = "file"
    LINK = "link"


class Resource(Base):
    """Resource model for the application"""

    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    title = Column(String(200), nullable=False)
    cover_image = Column(String(255), nullable=True)
    period = Column(Integer, nullable=False)
    file_url = Column(String(255), nullable=True)
    resource_type = Column(Enum(ResourceType), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now(UTC))
    updated_at = Column(
        DateTime,
        default=datetime.now(UTC),
        onupdate=datetime.now(UTC),
    )

    # Relationships
    class_ = relationship("ClassModel", back_populates="resources")
    creator = relationship("User", foreign_keys=[created_by])
