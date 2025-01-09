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
    auth_session_model = AuthSessionModel(
        user_id=user_id,
        user_ip=user_ip,
        user_agent=user_agent,
    )
    db.add(auth_session_model)
    await db.flush()
    return auth_session_model


async def get_auth_session(db: AsyncSession, auth_session_id: UUID, user_id: int) -> AuthSessionSchema:
    auth_session_model = await get_auth_session_model(db, session_id=auth_session_id, user_id=user_id)
    return AuthSessionSchema.model_construct(**auth_session_model.to_dict())


async def delete_auth_session(db: AsyncSession, redis: Redis, session: UUID | AuthSessionModel, user_id: int) -> None:
    auth_session_model = (
        session
        if isinstance(session, AuthSessionModel)
        else (await get_auth_session_model(db, session_id=session, user_id=user_id))
    )
    await redis.delete(AuthRedisKeyType.access.format(auth_session_model.access_token))
    await db.delete(auth_session_model)
    await db.flush()
