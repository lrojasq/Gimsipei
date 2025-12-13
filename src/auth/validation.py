from pydantic import BaseModel, constr


class LoginSchema(BaseModel):
    username: str
    password: str


class CreateFirstAdminSchema(BaseModel):
    username: constr(min_length=3, max_length=50)
    password: constr(min_length=6)
    full_name: constr(max_length=100)
    document: constr(min_length=1, max_length=20)
    secret_key: str


class ForgotPasswordSchema(BaseModel):
    username: str
    new_password: constr(min_length=6)
