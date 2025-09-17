from pydantic import BaseModel, constr, validator
from typing import Optional
from datetime import datetime


class CourseCreateSchema(BaseModel):
    academic_year: constr(min_length=9, max_length=9)  # "2024-2025"
    period: int
    grade_level: constr(min_length=1, max_length=50)
    name: constr(min_length=1, max_length=100)

    @validator("period", pre=True)
    def convert_period_to_int(cls, v):
        if isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                raise ValueError("El período debe ser un número válido")
        return v

    @validator("academic_year")
    def validate_academic_year(cls, v):
        # Validar formato YYYY-YYYY
        if not v.count("-") == 1:
            raise ValueError("El año académico debe tener el formato YYYY-YYYY")
        parts = v.split("-")
        if len(parts[0]) != 4 or len(parts[1]) != 4:
            raise ValueError("El año académico debe tener el formato YYYY-YYYY")
        try:
            int(parts[0])
            int(parts[1])
        except ValueError:
            raise ValueError("El año académico debe contener solo números")
        return v

    @validator("period")
    def validate_period(cls, v):
        if v not in [1, 2, 3]:
            raise ValueError("El período debe ser 1, 2 o 3")
        return v

    @validator("grade_level")
    def validate_grade_level(cls, v):
        valid_grades = ["Sexto", "Séptimo", "Octavo", "Noveno", "Décimo", "Undécimo"]
        if v not in valid_grades:
            raise ValueError(f"El grado debe ser uno de: {', '.join(valid_grades)}")
        return v


class CourseUpdateSchema(BaseModel):
    academic_year: Optional[constr(min_length=9, max_length=9)] = None
    period: Optional[int] = None
    grade_level: Optional[constr(min_length=1, max_length=50)] = None
    name: Optional[constr(min_length=1, max_length=100)] = None
    description: Optional[constr(max_length=255)] = None
    is_active: Optional[bool] = None

    @validator("period", pre=True)
    def convert_period_to_int(cls, v):
        if v is not None and isinstance(v, str):
            try:
                return int(v)
            except ValueError:
                raise ValueError("El período debe ser un número válido")
        return v

    @validator("academic_year")
    def validate_academic_year(cls, v):
        if v is not None:
            if not v.count("-") == 1:
                raise ValueError("El año académico debe tener el formato YYYY-YYYY")
            parts = v.split("-")
            if len(parts[0]) != 4 or len(parts[1]) != 4:
                raise ValueError("El año académico debe tener el formato YYYY-YYYY")
            try:
                int(parts[0])
                int(parts[1])
            except ValueError:
                raise ValueError("El año académico debe contener solo números")
        return v

    @validator("period")
    def validate_period(cls, v):
        if v is not None and v not in [1, 2, 3, 4, 5]:
            raise ValueError("El período debe ser 1, 2, 3, 4 o 5")
        return v

    @validator("grade_level")
    def validate_grade_level(cls, v):
        if v is not None:
            valid_grades = [
                "Sexto",
                "Séptimo",
                "Octavo",
                "Noveno",
                "Décimo",
                "Undécimo",
            ]
            if v not in valid_grades:
                raise ValueError(f"El grado debe ser uno de: {', '.join(valid_grades)}")
        return v


class CourseResponseSchema(BaseModel):
    id: int
    academic_year: str
    period: int
    grade_level: str
    name: str
    description: Optional[str]
    is_active: bool
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class CourseStudentSchema(BaseModel):
    student_id: int
    is_active: bool = True


class CourseSubjectSchema(BaseModel):
    subject_id: int
    teacher_id: int
    is_active: bool = True
