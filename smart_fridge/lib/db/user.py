from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from smart_fridge.core.exceptions.user import UserEmailAlreadyExistsException, UserNotFoundException
from smart_fridge.core.security import Encryptor
from smart_fridge.lib.models import UserModel
from smart_fridge.lib.schemas.user import UserCreateSchema, UserSchema


async def is_email_exists(db: AsyncSession, email: str) -> bool:
    query = select(UserModel).where(UserModel.email == email, UserModel.deleted_at.is_(None))
    return bool((await db.execute(query)).scalar_one_or_none())


async def raise_for_user_email(db: AsyncSession, email: str) -> None:
    if await is_email_exists(db, email):
        raise UserEmailAlreadyExistsException(email=email)


async def create_user(
    db: AsyncSession,
    *,
    schema: UserCreateSchema,
) -> UserSchema:
    await raise_for_user_email(db, schema.email)

    hashed_password = Encryptor.hash_password(schema.password)
    user_model = UserModel(
        **schema.model_dump(exclude={"password"}),
        hashed_password=hashed_password,
    )
    db.add(user_model)
    await db.flush()
    return UserSchema.model_construct(**user_model.to_dict())


async def get_user_model(
    db: AsyncSession,
    *,
    email: str,
) -> UserModel:
    query = select(UserModel).where(UserModel.email == email)
    result = (await db.execute(query)).scalar_one_or_none()
    if result is None:
        raise UserNotFoundException
    return result


async def get_user_model_by_id(
    db: AsyncSession,
    *,
    user_id: int,
) -> UserModel:
    query = select(UserModel).where(UserModel.id == user_id)
    result = (await db.execute(query)).scalar_one_or_none()
    if result is None:
        raise UserNotFoundException
    return result


async def get_user(
    db: AsyncSession,
    *,
    user_id: int,
) -> UserSchema:
    query = select(UserModel).where(UserModel.id == user_id)
    user_model = (await db.execute(query)).scalar_one_or_none()
    if user_model is None:
        raise UserNotFoundException
    return UserSchema.model_construct(**user_model.to_dict())


async def delete_user(
    db: AsyncSession,
    *,
    user_id: int,
) -> None:
    user_model = await get_user_model_by_id(db, user_id=user_id)
    user_model.deleted_at = datetime.now(timezone.utc)

    await db.flush()
