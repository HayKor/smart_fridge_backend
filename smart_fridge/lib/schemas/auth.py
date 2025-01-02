from uuid import UUID

from .abc import BaseSchema


class TokenRedisData(BaseSchema):
    session_id: UUID
    user_id: int
    encryption_key: str


class TokenCreateSchema(BaseSchema):
    email: str
    password: str


class TokenSchema(BaseSchema):
    access_token: str
    refresh_token: str
    access_token_expires_in: int
    refresh_token_expires_in: int
