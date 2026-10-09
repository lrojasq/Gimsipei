from datetime import datetime

from pydantic import BaseModel, constr


class SubjectCreateSchema(BaseModel):
    name: constr(min_length=1, max_length=100)


class SubjectUpdateSchema(BaseModel):
    name: constr(min_length=1, max_length=100) | None = None


class SubjectResponseSchema(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
