from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, List


class EvaluationCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    period: int = Field(..., ge=1, le=4)
    course_id: int = Field(..., gt=0)
    subject_id: int = Field(..., gt=0)


class EvaluationUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    period: Optional[int] = Field(None, ge=1, le=4)
    course_id: Optional[int] = Field(None, gt=0)
    subject_id: Optional[int] = Field(None, gt=0)


class EvaluationQuestionPayload(BaseModel):
    """Schema para una pregunta de la evaluación (usado en el modal dinámico)."""

    text: str = Field(..., min_length=1)
    type: str = Field(..., regex="^(open|multi)$")
    options: Dict[str, str] = Field(default_factory=dict)
    answer: Optional[str] = None

    @validator("options", pre=True, always=True)
    def normalize_options(cls, v):
        return v or {}

    @validator("answer", always=True)
    def validate_answer(cls, v, values):
        qtype = values.get("type")
        options = values.get("options") or {}
        if qtype == "multi":
            # Mínimo 4 y máximo 4 opciones y una respuesta válida
            if len(options) < 4:
                raise ValueError(
                    "Las preguntas de opción múltiple deben tener al menos 4 opciones"
                )
            if len(options) > 4:
                raise ValueError(
                    "Las preguntas de opción múltiple no pueden tener más de 4 opciones"
                )
            if not v or v not in options:
                raise ValueError(
                    "Las preguntas de opción múltiple deben tener una respuesta correcta válida"
                )
        return v


class EvaluationWithQuestionsCreateSchema(EvaluationCreateSchema):
    """Schema extendido para crear evaluación con preguntas."""

    questions: List[EvaluationQuestionPayload] = Field(..., min_items=2, max_items=10)
