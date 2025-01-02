from datetime import datetime

from .abc import BaseSchema


class BaseUserSchema(BaseSchema):
    username: str
    email: str


class UserCreateSchema(BaseUserSchema):
    password: str


class UserSchema(BaseUserSchema):
    id: int
    hashed_password: str
    is_active: bool
    created_at: datetime
