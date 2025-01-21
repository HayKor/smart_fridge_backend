from datetime import datetime, timezone
from typing import AsyncGenerator

from sqlalchemy import asc, extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_fridge.core.exceptions.user import UserEmailAlreadyExistsException, UserNotFoundException
from smart_fridge.core.security import Encryptor
from smart_fridge.lib.models import UserModel
from smart_fridge.lib.models.product import ProductModel
from smart_fridge.lib.models.product_type import ProductTypeModel
from smart_fridge.lib.schemas.user import UserCreateSchema, UserPatchSchema, UserSchema, UserUpdateSchema


async def is_email_exists(db: AsyncSession, email: str) -> bool:
    query = select(UserModel).where(UserModel.email == email, UserModel.deleted_at.is_(None))
    return bool((await db.execute(query)).scalar_one_or_none())


async def raise_for_user_email(db: AsyncSession, email: str) -> None:
    if await is_email_exists(db, email):
        raise UserEmailAlreadyExistsException(email=email)


async def create_user(db: AsyncSession, *, schema: UserCreateSchema) -> UserSchema:
    await raise_for_user_email(db, schema.email)

    hashed_password = Encryptor.hash_password(schema.password)
    user_model = UserModel(
        **schema.model_dump(exclude={"password"}),
        hashed_password=hashed_password,
    )
    db.add(user_model)
    await db.flush()
    return UserSchema.model_construct(**user_model.to_dict())


async def get_user_model(db: AsyncSession, *, email: str) -> UserModel:
    query = select(UserModel).where(UserModel.email == email)
    result = (await db.execute(query)).scalar_one_or_none()
    if result is None:
        raise UserNotFoundException
    return result


async def get_user_model_by_id(db: AsyncSession, *, user_id: int) -> UserModel:
    query = select(UserModel).where(UserModel.id == user_id)
    result = (await db.execute(query)).scalar_one_or_none()
    if result is None:
        raise UserNotFoundException
    return result


async def get_user(db: AsyncSession, *, user_id: int) -> UserSchema:
    user_model = await get_user_model_by_id(db, user_id=user_id)
    return UserSchema.model_construct(**user_model.to_dict())


async def update_user(db: AsyncSession, *, user_id: int, schema: UserUpdateSchema | UserPatchSchema) -> UserSchema:
    user_model = await get_user_model_by_id(db, user_id=user_id)

    if schema.email and schema.email != user_model.email:
        await raise_for_user_email(db, schema.email)

    for field, value in schema.iterate_set_fields():
        setattr(user_model, field, value)

    await db.flush()
    return UserSchema.model_construct(**user_model.to_dict())


async def delete_user(db: AsyncSession, *, user_id: int) -> None:
    user_model = await get_user_model_by_id(db, user_id=user_id)
    user_model.deleted_at = datetime.now(timezone.utc)

    await db.flush()


async def get_user_tg_id_and_day_count(db: AsyncSession, user_id: int) -> tuple[int | None, int | None]:
    user_model = await get_user_model_by_id(db, user_id=user_id)
    query = (
        select(
            extract(
                "day", (ProductModel.manufactured_at + ProductTypeModel.exp_period_before_opening) - func.now()
            ).label("days"),
        )
        .select_from(UserModel)
        .join(UserModel.products)
        .join(ProductModel.product_type)
        .where(UserModel.id == user_id)
        .order_by(asc("days"))
        .limit(1)
    )
    delta_days = (await db.execute(query)).scalar_one_or_none()

    return user_model.tg_id, delta_days


async def get_expiry_users(db: AsyncSession) -> AsyncGenerator[tuple[int, int], None]:
    query = select(UserModel)
    users = (await db.execute(query)).scalars().all()
    for user in users:
        tg_id, delta_days = await get_user_tg_id_and_day_count(db, user.id)
        if delta_days is None or delta_days >= 2 or tg_id is None:
            continue
        yield tg_id, delta_days
