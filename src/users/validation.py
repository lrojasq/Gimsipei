from pydantic import BaseModel, constr, validator
from typing import Optional
from src.models.user import UserRole


class UserCreateSchema(BaseModel):
    username: constr(min_length=3, max_length=50)
    document: constr(min_length=1, max_length=20)
    password: constr(min_length=6)
    full_name: Optional[constr(max_length=100)] = None
    avatar: Optional[str] = None
    role: UserRole


class StudentCreateSchema(BaseModel):
    """Schema para crear un estudiante con validaciones específicas"""

    username: constr(min_length=3, max_length=50)
    document: constr(min_length=1, max_length=20)
    password: constr(min_length=6)
    full_name: Optional[constr(max_length=100)] = None
    avatar: Optional[str] = None
    course_id: Optional[int] = None

    @validator("course_id", pre=True)
    @classmethod
    def validate_course_id(cls, v):
        """Valida y convierte course_id a entero positivo si está presente"""
        if v is None or v == "":
            return None
        try:
            course_id = int(v)
            if course_id <= 0:
                raise ValueError("course_id debe ser un entero positivo")
            return course_id
        except (ValueError, TypeError):
            raise ValueError("course_id debe ser un entero válido")

    def to_user_create_schema(self) -> UserCreateSchema:
        """Convierte este schema a UserCreateSchema con rol STUDENT"""
        return UserCreateSchema(
            username=self.username,
            document=self.document,
            password=self.password,
            full_name=self.full_name,
            avatar=self.avatar,
            role=UserRole.STUDENT,
        )


class UserUpdateSchema(BaseModel):
    username: Optional[constr(min_length=3, max_length=50)] = None
    document: Optional[constr(min_length=1, max_length=20)] = None
    password: Optional[constr(min_length=6)] = None
    full_name: Optional[constr(max_length=100)] = None
    avatar: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserResponseSchema(BaseModel):
    id: int
    username: str
    document: Optional[str]
    full_name: Optional[str]
    avatar: Optional[str] = None
    role: str
    is_active: bool

    class Config:
        json_encoders = {UserRole: lambda v: v.value}
