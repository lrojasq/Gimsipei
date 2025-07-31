from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from src.database.database import Base
from enum import Enum as PyEnum
from datetime import datetime


class ResourceType(PyEnum):
    FILE = "file"
    LINK = "link"


class Resource(Base):
    """Resource model for the application"""

    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)
    file_url = Column(String(255), nullable=True)
    link = Column(String(255), nullable=True)
    resource_type = Column(Enum(ResourceType), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    class_ = relationship("ClassModel", back_populates="resources")
