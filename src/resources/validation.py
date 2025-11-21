from pydantic import BaseModel, constr, conint
from typing import Optional
from datetime import datetime


class ResourceCreateSchema(BaseModel):
    class_id: int
    title: constr(min_length=1, max_length=200)
    period: conint(ge=1, le=4)
    resource_type: str = "file"  # "file" or "link"
    file_url: Optional[str] = None


class ResourceUpdateSchema(BaseModel):
    title: Optional[constr(min_length=1, max_length=200)] = None
    period: Optional[conint(ge=1, le=4)] = None
    file_url: Optional[str] = None


class ResourceResponseSchema(BaseModel):
    id: int
    class_id: int
    title: str
    cover_image: Optional[str]
    period: int
    file_url: Optional[str]
    resource_type: str
    created_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
