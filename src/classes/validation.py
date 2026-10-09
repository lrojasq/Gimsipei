from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class ResourceType(str, Enum):
    FILE = "FILE"
    LINK = "LINK"


# Subject Schemas
class SubjectBase(BaseModel):
    name: str
    description: str | None = None


class SubjectCreate(SubjectBase):
    teacher_id: int


class SubjectUpdate(SubjectBase):
    name: str | None = None
    teacher_id: int


class SubjectInDB(SubjectBase):
    id: int
    teacher_id: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Class Schemas
class ClassBase(BaseModel):
    title: str
    description: str | None = None
    class_number: int
    date: datetime


class ClassCreate(ClassBase):
    created_by: int


class ClassUpdate(ClassBase):
    title: str | None = None
    description: str | None = None
    class_number: int | None = None
    date: datetime | None = None


class ClassInDB(ClassBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Resource Schemas
class ResourceBase(BaseModel):
    class_id: int
    file_url: str | None = None
    link: str | None = None
    resource_type: ResourceType


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(ResourceBase):
    file_url: str | None = None
    link: str | None = None
    resource_type: ResourceType | None = None


class ResourceInDB(ResourceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# ClassView Schemas
class ClassViewBase(BaseModel):
    class_id: int
    student_id: int


class ClassViewCreate(ClassViewBase):
    pass


class ClassViewInDB(ClassViewBase):
    id: int
    viewed_at: datetime

    class Config:
        orm_mode = True
