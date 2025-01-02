from datetime import datetime
from uuid import UUID

from .abc import BaseSchema


class BaseAuthSessionSchema(BaseSchema):
    user_ip: str
    user_agent: str | None


class AuthSessionSchema(BaseAuthSessionSchema):
    id: UUID
    last_online: datetime
    created_at: datetime
