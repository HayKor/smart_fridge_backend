from datetime import datetime, timezone
from uuid import UUID, uuid4

from jwt import encode as jwt_encode

from . import fields as f
from .abc import BaseSchema
from .user import USER_EMAIL, USER_PASSWORD


TOKEN = f.BaseField(
    description="JSON Web Token.",
    examples=[jwt_encode({"sub": str(uuid4()), "exp": datetime.now(timezone.utc)}, "SECRET_KEY")],
)
TOKEN_EXPIRATION = f.BaseField(description="Token expiration in minutes.", ge=5, le=525600, examples=[43800])
FINGERPRINT = f.BaseField(
    description="Fingerprint.", min_length=32, max_length=64, examples=["f1b7e156414663c4b81fbadadedcf01f"]
)


class TokenRedisData(BaseSchema):
    session_id: UUID
    user_id: int
    encryption_key: str


class TokenCreateSchema(BaseSchema):
    email: str = USER_EMAIL
    password: str = USER_PASSWORD


class TokenSchema(BaseSchema):
    access_token: str = TOKEN
    refresh_token: str = TOKEN
    access_token_expires_in: int = TOKEN_EXPIRATION
    refresh_token_expires_in: int = TOKEN_EXPIRATION
