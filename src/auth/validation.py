from pydantic import BaseModel, EmailStr, constr, ValidationError
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    TEACHER = "TEACHER"
    STUDENT = "STUDENT"


class LoginSchema(BaseModel):
    username: str
    password: str


class CreateFirstAdminSchema(BaseModel):
    email: EmailStr
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=6)
    full_name: constr(max_length=100)
    secret_key: str  # Para validar la creación del primer admin
