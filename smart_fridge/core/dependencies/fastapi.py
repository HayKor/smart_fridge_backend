from typing import Annotated, Any, AsyncGenerator
from uuid import UUID

from fastapi import Cookie, Depends, Header, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import ConnectionPool, Redis as AbstractRedis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from smart_fridge.core.config import AppConfig
from smart_fridge.lib.schemas.auth import TokenRedisData

from ..security import Encryptor
from . import constructors as app_depends


def db_session_maker_stub() -> sessionmaker[Any]:
    raise NotImplementedError


def app_config_stub() -> AppConfig:
    raise NotImplementedError


async def db_session(
    request: Request,
    maker: Annotated[sessionmaker[Any], Depends(db_session_maker_stub)],
) -> AsyncGenerator[AsyncSession, None]:
    generator = app_depends.db_session_autocommit(maker)
    session = await anext(generator)
    request.state.db = session

    yield session

    try:
        await anext(generator)
    except StopAsyncIteration:
        pass
    else:
        raise RuntimeError("Database session not closed (db dependency generator is not closed).")


def redis_conn_pool_stub() -> ConnectionPool:
    raise NotImplementedError


async def redis_conn(
    request: Request, conn_pool: Annotated[ConnectionPool, Depends(redis_conn_pool_stub)]
) -> AsyncGenerator[AbstractRedis, None]:
    generator = app_depends.redis_conn(conn_pool)
    redis = await anext(generator)
    request.state.redis = redis

    yield redis

    try:
        await anext(generator)
    except StopAsyncIteration:
        pass
    else:
        raise RuntimeError("Redis session not closed (redis dependency generator is not closed).")


def encryptor(config: Annotated[AppConfig, Depends(app_depends.app_config)]) -> Encryptor:
    return app_depends.encryptor(config)


def get_client_host(request: Request) -> str:
    client = request.client
    return client.host if client else ""


async def get_token_data(
    encryptor: Annotated[Encryptor, Depends(encryptor)],
    redis: Annotated[AbstractRedis, Depends(redis_conn)],
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer())],
) -> TokenRedisData:
    return await app_depends.get_token_data(encryptor, redis, credentials.credentials)


def get_refresh_token(
    encryptor: Annotated[Encryptor, Depends(encryptor)],
    refresh_token: Annotated[str | None, Cookie()],
) -> UUID:
    return app_depends.get_refresh_token(encryptor, refresh_token or "")


ClientHostDependency = Annotated[str, Depends(get_client_host)]
UserAgentDependency = Annotated[str, Header()]
TokenDataDependency = Annotated[TokenRedisData, Depends(get_token_data)]
RefreshTokenDependency = Annotated[UUID, Depends(get_refresh_token)]
EncryptorDependency = Annotated[Encryptor, Depends(encryptor)]
DatabaseDependency = Annotated[AsyncSession, Depends(db_session)]
RedisDependency = Annotated[AbstractRedis, Depends(redis_conn)]
