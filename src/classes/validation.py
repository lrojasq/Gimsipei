from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class ResourceType(str, Enum):
    FILE = "FILE"
    LINK = "LINK"


# Subject Schemas
class SubjectBase(BaseModel):
    name: str
    description: Optional[str] = None


class SubjectCreate(SubjectBase):
    teacher_id: int


class SubjectUpdate(SubjectBase):
    name: Optional[str] = None
    teacher_id: int


class SubjectInDB(SubjectBase):
    id: int
    teacher_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Class Schemas
class ClassBase(BaseModel):
    title: str
    description: Optional[str] = None
    class_number: int
    date: datetime


class ClassCreate(ClassBase):
    created_by: int


class ClassUpdate(ClassBase):
    title: Optional[str] = None
    description: Optional[str] = None
    class_number: Optional[int] = None
    date: Optional[datetime] = None


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
    file_url: Optional[str] = None
    link: Optional[str] = None
    resource_type: ResourceType


class ResourceCreate(ResourceBase):
    pass


class ResourceUpdate(ResourceBase):
    file_url: Optional[str] = None
    link: Optional[str] = None
    resource_type: Optional[ResourceType] = None


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
