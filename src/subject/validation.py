from typing import Optional

from pydantic import BaseModel, constr, validator
from datetime import datetime


class SubjectCreateSchema(BaseModel):
    name: constr(min_length=1, max_length=100)
    teacher_id: int

    @validator("teacher_id")
    def validate_teacher_id(cls, v):
        if v <= 0:
            raise ValueError("El ID del profesor debe ser válido")
        return v


class SubjectUpdateSchema(BaseModel):
    name: Optional[constr(min_length=1, max_length=100)] = None
    teacher_id: Optional[int] = None

    @validator("teacher_id")
    def validate_teacher_id(cls, v):
        if v is not None and v <= 0:
            raise ValueError("El ID del profesor debe ser válido")
        return v


class SubjectResponseSchema(BaseModel):
    id: int
    name: str
    teacher_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
