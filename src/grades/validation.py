from pydantic import BaseModel, Field, validator
from typing import Optional


class GradeCreateSchema(BaseModel):
    student_id: int = Field(..., gt=0)
    course_id: int = Field(..., gt=0)
    subject_id: int = Field(..., gt=0)
    period: int = Field(..., ge=1, le=4)
    tasks_grade: Optional[float] = Field(None, ge=0, le=5)
    assignments_grade: Optional[float] = Field(None, ge=0, le=5)
    evaluations_grade: Optional[float] = Field(None, ge=0, le=5)
    final_grade: Optional[float] = Field(None, ge=0, le=5)

    @validator("period")
    def validate_period(cls, v):
        if v not in [1, 2, 3, 4]:
            raise ValueError("Period must be 1, 2, 3, or 4")
        return v


class GradeUpdateSchema(BaseModel):
    tasks_grade: Optional[float] = Field(None, ge=0, le=5)
    assignments_grade: Optional[float] = Field(None, ge=0, le=5)
    evaluations_grade: Optional[float] = Field(None, ge=0, le=5)
    final_grade: Optional[float] = Field(None, ge=0, le=5)
