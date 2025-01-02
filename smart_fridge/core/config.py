import logging
from os import environ
from typing import Any, Self

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


logger = logging.getLogger(__name__)


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file_encoding="utf-8", env_nested_delimiter="__", extra="ignore")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        logger.debug(f"Config initialized: {self.model_dump()}")

    @classmethod
    def from_env(cls) -> Self:
        return cls(
            _env_file=environ.get("ENV_FILE", ".env"),
            _secrets_dir=environ.get("SECRETS_DIR"),
        )


class SecurityConfig(BaseSettings):
    secret_key: str


class JWTConfig(BaseSettings):
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=30)


class DatabaseConfig(BaseSettings):
    url: str


class RedisConfig(BaseSettings):
    url: str


class AppConfig(BaseConfig):
    security: SecurityConfig
    jwt: JWTConfig
    database: DatabaseConfig
    redis: RedisConfig
