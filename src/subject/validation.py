from typing import Optional

from pydantic import BaseModel, constr
from datetime import datetime


class SubjectCreateSchema(BaseModel):
    name: constr(min_length=1, max_length=100)


class SubjectUpdateSchema(BaseModel):
    name: Optional[constr(min_length=1, max_length=100)] = None


class SubjectResponseSchema(BaseModel):
    id: int
    name: str
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
