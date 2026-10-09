from datetime import datetime

from pydantic import BaseModel, conint, constr


class ResourceCreateSchema(BaseModel):
    class_id: int
    title: constr(min_length=1, max_length=200)
    period: conint(ge=1, le=4)
    resource_type: str = "file"  # "file" or "link"
    file_url: str | None = None


class ResourceUpdateSchema(BaseModel):
    title: constr(min_length=1, max_length=200) | None = None
    period: conint(ge=1, le=4) | None = None
    file_url: str | None = None


class ResourceResponseSchema(BaseModel):
    id: int
    class_id: int
    title: str
    cover_image: str | None
    period: int
    file_url: str | None
    resource_type: str
    created_by: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}
