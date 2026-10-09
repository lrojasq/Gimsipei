from pydantic import BaseModel, Field


class BookCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    description: str | None = Field("", max_length=1000)
    target_audience: str = Field(..., regex="^(STUDENT|TEACHER)$")


class BookUpdateSchema(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    author: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = Field(None, max_length=1000)
    target_audience: str | None = Field(None, regex="^(STUDENT|TEACHER)$")
