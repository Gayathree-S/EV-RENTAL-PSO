"""
User authentication and profile schemas.
"""

from pydantic import BaseModel, ConfigDict


class UserRegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class UserRegisterResponse(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserLoginRequest(BaseModel):
    email: str
    password: str


class UserLoginResponse(BaseModel):
    user_id: int
    name: str
    email: str
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


class UserOut(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)
