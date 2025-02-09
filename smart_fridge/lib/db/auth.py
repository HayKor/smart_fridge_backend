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
    """Raise an exception if the provided password does not match the hashed password.

    Args:
        password (str): The plain text password to check.
        password_hash (str): The hashed password to compare against.

    Raises:
        BadAuthDataException: If the passwords do not match.
    """
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
    """Create a new authentication token for the user.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        redis (Redis): Redis client for token storage.
        encryptor (Encryptor): Instance of the Encryptor for hashing and encoding.
        user_ip (str): IP address of the user.
        user_agent (str | None): User agent string of the user.
        schema (TokenCreateSchema): Schema containing user credentials.

    Returns:
        TokenSchema: Contains the generated access and refresh tokens and their expiration times.
    """
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
    db: AsyncSession, redis: Redis, encryptor: Encryptor, user_ip: str, user_agent: str | None, token_id: UUID
) -> TokenSchema:
    """Refresh the authentication token for the user.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        redis (Redis): Redis client for token storage.
        encryptor (Encryptor): Instance of the Encryptor for hashing and encoding.
        user_ip (str): IP address of the user.
        user_agent (str | None): User agent string of the user.
        token_id (UUID): The ID of the refresh token to be refreshed.

    Returns:
        TokenSchema: Contains the new access and refresh tokens and their expiration times.
    """
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
    """Create and store a new access token in Redis.

    Args:
        redis (Redis): Redis client for token storage.
        auth_session_model (AuthSessionModel): The authentication session model containing user information.
        access_token_id (UUID | None): Optional ID for the access token; generates a new one if not provided.
        expires_in (int): Expiration time in minutes for the access token.

    Returns:
        UUID: The ID of the created access token.
    """
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
