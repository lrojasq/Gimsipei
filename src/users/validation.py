from pydantic import BaseModel, constr
from typing import Optional
from src.models.user import UserRole


class UserCreateSchema(BaseModel):
    username: constr(min_length=3, max_length=50)
    document: constr(min_length=1, max_length=20)
    password: constr(min_length=6)
    full_name: Optional[constr(max_length=100)] = None
    role: UserRole


class UserUpdateSchema(BaseModel):
    username: Optional[constr(min_length=3, max_length=50)] = None
    document: Optional[constr(min_length=1, max_length=20)] = None
    password: Optional[constr(min_length=6)] = None
    full_name: Optional[constr(max_length=100)] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponseSchema(BaseModel):
    id: int
    username: str
    document: Optional[str]
    full_name: Optional[str]
    role: str
    is_active: bool

    class Config:
        json_encoders = {UserRole: lambda v: v.value}
