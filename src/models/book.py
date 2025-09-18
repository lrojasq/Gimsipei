from sqlalchemy import Column, Integer, String, Text
from src.database.database import Base


class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    description = Column(Text, default="")
    file_path = Column(String(512), nullable=False)
    cover_image = Column(String(512), nullable=True)
    target_audience = Column(String(20), nullable=False)
