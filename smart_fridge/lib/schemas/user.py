from datetime import datetime

from pydantic import EmailStr

from . import fields as f
from .abc import BaseSchema


USER_ID = f.ID(description="User ID")
USERNAME = f.BaseField(description="User's username", examples=["pussydestroyer100"])
USER_EMAIL = f.BaseField(description="User's email", examples=["pussydestroyer100@gmail.com"])
USER_PASSWORD = f.BaseField(description="User's password when creating an account", examples=["qwerty"])
USER_HASHED_PASSWORD = f.BaseField(description="User's hashed password", examples=["1g318chdua14uhjdsf"])
USER_IS_ACTIVE = f.BaseField(description="Whether user is not banned or is")
USER_CREATED_AT = f.DATETIME(description="User account creation date")
USER_DELETED_AT = f.DATETIME(description="User account deletion date")
USER_TG_ID = f.ID(description="User's telegram ID.")


class BaseUserSchema(BaseSchema):
    username: str = USERNAME
    email: EmailStr = USER_EMAIL


class UserCreateSchema(BaseUserSchema):
    password: str = USER_PASSWORD


class UserUpdateSchema(BaseUserSchema):
    pass


class UserPatchSchema(UserUpdateSchema):
    email: str = USER_EMAIL(default=None)
    username: str = USERNAME(default=None)
    tg_id: int = USER_TG_ID(default=None)


class UserSchema(BaseUserSchema):
    id: int = USER_ID
    hashed_password: str = USER_HASHED_PASSWORD
    is_active: bool = USER_IS_ACTIVE
    tg_id: int = USER_TG_ID
    created_at: datetime = USER_CREATED_AT
    deleted_at: datetime | None = USER_DELETED_AT
