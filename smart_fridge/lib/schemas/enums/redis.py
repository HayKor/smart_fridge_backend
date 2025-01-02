from .abc import BaseEnum


class BaseRedisKeyType(BaseEnum):
    """Redis key types."""


class AuthRedisKeyType(BaseRedisKeyType):
    """Redis auth key type."""

    _prefix = "auth"

    access = f"{_prefix}:access:{{}}"
