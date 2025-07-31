from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from src.models.user import UserRole
from enum import Enum


class UserCreateSchema(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=6)
    full_name: Optional[constr(max_length=100)] = None
    role: UserRole


class UserUpdateSchema(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[constr(min_length=3, max_length=50)] = None
    password: Optional[constr(min_length=6)] = None
    full_name: Optional[constr(max_length=100)] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponseSchema(BaseModel):
    id: int
    email: str
    username: str
    full_name: Optional[str]
    role: str
    is_active: bool

    class Config:
        json_encoders = {UserRole: lambda v: v.value}
