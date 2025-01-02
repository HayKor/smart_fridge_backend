from secrets import compare_digest
from uuid import UUID, uuid4

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from smart_fridge.core.exceptions.auth import BadAuthDataException
from smart_fridge.core.security import Encryptor
from smart_fridge.lib.db import auth_session as auth_session_db, user as user_db
from smart_fridge.lib.models import AuthSessionModel
from smart_fridge.lib.schemas.auth import TokenCreateSchema, TokenRedisData, TokenSchema
from smart_fridge.lib.schemas.enums.redis import AuthRedisKeyType


def raise_user_password(password: str, password_hash: str) -> None:
    hashed_password = Encryptor.hash_password(password)
    if not compare_digest(hashed_password, password_hash):
        raise BadAuthDataException


async def create_token(
    db: AsyncSession,
    redis: Redis,
    encryptor: Encryptor,
    user_ip: str,
    user_agent: str | None,
    schema: TokenCreateSchema,
) -> TokenSchema:
    user_model = await user_db.get_user_model(db, email=schema.email)
    raise_user_password(schema.password, user_model.hashed_password)

    auth_session_model = await auth_session_db.create_auth_session(
        db,
        user_id=user_model.id,
        user_ip=user_ip,
        user_agent=user_agent,
    )

    await _create_access_token(
        redis,
        auth_session_model,
        access_token_id=auth_session_model.access_token,
        expires_in=encryptor.jwt_expire_minutes,
    )

    return TokenSchema(
        access_token=encryptor.encode_jwt(auth_session_model.access_token),
        refresh_token=encryptor.encode_jwt(
            auth_session_model.refresh_token,
            expires_in=encryptor.jwt_refresh_expire_days,
        ),
        access_token_expires_in=encryptor.jwt_expire_minutes,
        refresh_token_expires_in=encryptor.jwt_refresh_expire_days,
    )


async def refresh_token(
    db: AsyncSession,
    redis: Redis,
    encryptor: Encryptor,
    user_ip: str,
    user_agent: str | None,
    token_id: UUID,
) -> TokenSchema:
    auth_session_model = await auth_session_db.get_auth_session_model(
        db,
        refresh_token=token_id,
        join_user=True,
    )

    await redis.delete(AuthRedisKeyType.access.format(auth_session_model.access_token))

    auth_session_model.user_ip = user_ip
    auth_session_model.user_agent = user_agent

    auth_session_model.access_token = await _create_access_token(
        redis, auth_session_model, expires_in=encryptor.jwt_expire_minutes
    )
    auth_session_model.refresh_token = uuid4()
    await db.flush()

    return TokenSchema(
        access_token=encryptor.encode_jwt(auth_session_model.access_token),
        refresh_token=encryptor.encode_jwt(
            auth_session_model.refresh_token,
            expires_in=encryptor.jwt_refresh_expire_days,
        ),
        access_token_expires_in=encryptor.jwt_expire_minutes,
        refresh_token_expires_in=encryptor.jwt_refresh_expire_days,
    )


async def _create_access_token(
    redis: Redis, auth_session_model: AuthSessionModel, *, access_token_id: UUID | None = None, expires_in: int = 30
) -> UUID:
    access_token_id = access_token_id or uuid4()
    await redis.set(
        AuthRedisKeyType.access.format(access_token_id),
        TokenRedisData(
            session_id=auth_session_model.id,
            user_id=auth_session_model.user_id,
            encryption_key=Encryptor.hash_password(auth_session_model.user.hashed_password[-32:], digest_size=32),
        ).model_dump_json(),
        ex=expires_in * 60,
    )
    return access_token_id
