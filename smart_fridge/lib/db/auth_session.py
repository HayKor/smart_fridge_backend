from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from smart_fridge.core.exceptions.auth_session import AuthSessionNotFoundException
from smart_fridge.lib.models import AuthSessionModel
from smart_fridge.lib.schemas.auth_session import AuthSessionSchema
from smart_fridge.lib.schemas.enums.redis import AuthRedisKeyType


async def get_auth_session_model(
    db: AsyncSession,
    *,
    session_id: UUID | None = None,
    user_id: int | None = None,
    refresh_token: UUID | None = None,
    join_user: bool = False,
) -> AuthSessionModel:
    """Retrieve an authentication session model from the database.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        session_id (UUID | None): Optional session ID to filter the query.
        user_id (int | None): Optional user ID to filter the query.
        refresh_token (UUID | None): Optional refresh token to filter the query.
        join_user (bool): Flag to indicate whether to join the user model.

    Returns:
        AuthSessionModel: The authentication session model.

    Raises:
        AuthSessionNotFoundException: If no matching authentication session is found.
    """
    query = select(AuthSessionModel)
    if session_id:
        query = query.where(AuthSessionModel.id == session_id, AuthSessionModel.user_id == user_id)
    if refresh_token:
        query = query.where(AuthSessionModel.refresh_token == refresh_token)
    if join_user:
        join_query = [joinedload(AuthSessionModel.user)]
        query = query.options(*join_query)

    result = (await db.execute(query)).scalar_one_or_none()

    if result is None:
        raise AuthSessionNotFoundException

    return result


async def create_auth_session(db: AsyncSession, user_id: int, user_ip: str, user_agent: str | None) -> AuthSessionModel:
    """Create a new authentication session in the database.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        user_id (int): ID of the user for whom the session is created.
        user_ip (str): IP address of the user.
        user_agent (str | None): User agent string of the user's device.

    Returns:
        AuthSessionModel: The created authentication session model.
    """
    auth_session_model = AuthSessionModel(
        user_id=user_id,
        user_ip=user_ip,
        user_agent=user_agent,
    )
    db.add(auth_session_model)
    await db.flush()
    return auth_session_model


async def get_auth_session(db: AsyncSession, auth_session_id: UUID, user_id: int) -> AuthSessionSchema:
    """Retrieve an authentication session schema by its ID.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        auth_session_id (UUID): ID of the authentication session to retrieve.
        user_id (int): ID of the user associated with the session.

    Returns:
        AuthSessionSchema: The authentication session schema.
    """
    auth_session_model = await get_auth_session_model(db, session_id=auth_session_id, user_id=user_id)
    return AuthSessionSchema.model_construct(**auth_session_model.to_dict())


async def delete_auth_session(db: AsyncSession, redis: Redis, session: UUID | AuthSessionModel, user_id: int) -> None:
    """Delete an authentication session from the database and Redis.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        redis (Redis): Redis client for session management.
        session (UUID | AuthSessionModel): The session ID or the session model to delete.
        user_id (int): ID of the user associated with the session.

    Raises:
        AuthSessionNotFoundException: If the session cannot be found.
    """
    auth_session_model = (
        session
        if isinstance(session, AuthSessionModel)
        else (await get_auth_session_model(db, session_id=session, user_id=user_id))
    )
    await redis.delete(AuthRedisKeyType.access.format(auth_session_model.access_token))
    await db.delete(auth_session_model)
    await db.flush()
