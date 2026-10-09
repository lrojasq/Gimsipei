from datetime import datetime

from pydantic import BaseModel, constr


class CourseCreateSchema(BaseModel):
    name: constr(min_length=1, max_length=100)


class CourseUpdateSchema(BaseModel):
    name: constr(min_length=1, max_length=100) | None = None
    description: constr(max_length=255) | None = None


class CourseResponseSchema(BaseModel):
    id: int
    academic_year: str
    name: str
    description: str | None
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
