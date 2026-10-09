from pydantic import BaseModel, constr, validator

from src.models.user import UserRole


class UserCreateSchema(BaseModel):
    username: constr(min_length=3, max_length=50)
    document: constr(min_length=1, max_length=20)
    password: constr(min_length=6)
    full_name: constr(max_length=100) | None = None
    avatar: str | None = None
    role: UserRole


class StudentCreateSchema(BaseModel):
    """Schema para crear un estudiante con validaciones específicas"""

    username: constr(min_length=3, max_length=50)
    document: constr(min_length=1, max_length=20)
    password: constr(min_length=6)
    full_name: constr(max_length=100) | None = None
    avatar: str | None = None
    course_id: int | None = None

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
        except (ValueError, TypeError) as err:
            raise ValueError("course_id debe ser un entero válido") from err

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
    username: constr(min_length=3, max_length=50) | None = None
    document: constr(min_length=1, max_length=20) | None = None
    password: constr(min_length=6) | None = None
    full_name: constr(max_length=100) | None = None
    avatar: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UserResponseSchema(BaseModel):
    id: int
    username: str
    document: str | None
    full_name: str | None
    avatar: str | None = None
    role: str
    is_active: bool

    class Config:
        json_encoders = {UserRole: lambda v: v.value}
