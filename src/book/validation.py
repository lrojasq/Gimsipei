from pydantic import BaseModel, Field
from typing import Optional


class BookCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field("", max_length=1000)
    target_audience: str = Field(..., regex="^(STUDENT|TEACHER)$")


class BookUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    target_audience: Optional[str] = Field(None, regex="^(STUDENT|TEACHER)$")
