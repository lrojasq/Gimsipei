from pydantic import BaseModel, constr
from typing import Optional
from datetime import datetime


class CourseCreateSchema(BaseModel):
    name: constr(min_length=1, max_length=100)


class CourseUpdateSchema(BaseModel):
    name: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[constr(max_length=255)] = None


class CourseResponseSchema(BaseModel):
    id: int
    academic_year: str
    name: str
    description: Optional[str]
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class CourseStudentSchema(BaseModel):
    student_id: int


class CourseSubjectSchema(BaseModel):
    subject_id: int
    teacher_id: int
    is_active: bool = True
