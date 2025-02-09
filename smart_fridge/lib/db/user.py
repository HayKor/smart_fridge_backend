from datetime import datetime, timezone
from typing import AsyncGenerator, Sequence

from sqlalchemy import asc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_fridge.core.exceptions.user import UserEmailAlreadyExistsException, UserNotFoundException
from smart_fridge.core.security import Encryptor
from smart_fridge.lib.models import UserModel
from smart_fridge.lib.models.fridge_product import FridgeProductModel
from smart_fridge.lib.models.product import ProductModel
from smart_fridge.lib.models.product_type import ProductTypeModel
from smart_fridge.lib.schemas.user import UserCreateSchema, UserPatchSchema, UserSchema, UserUpdateSchema


async def is_email_exists(db: AsyncSession, email: str) -> bool:
    """Check if user email already exists.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        email (str): User email.

    Returns:
        bool: True if email exists, False otherwise.
    """
    query = select(UserModel).where(UserModel.email == email, UserModel.deleted_at.is_(None))
    return bool((await db.execute(query)).scalar_one_or_none())


async def raise_for_user_email(db: AsyncSession, email: str) -> None:
    """Raise an exception if the user email already exists.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        email (str): User email to check.

    Raises:
        UserEmailAlreadyExistsException: If the email already exists.
    """
    if await is_email_exists(db, email):
        raise UserEmailAlreadyExistsException(email=email)


async def create_user(db: AsyncSession, *, schema: UserCreateSchema) -> UserSchema:
    """Create a new user in the database.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        schema (UserCreateSchema): User creation schema containing user data.

    Returns:
        UserSchema: The created user schema.
    """
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
    """Retrieve a user model by email.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        email (str): User email.

    Returns:
        UserModel: The user model.

    Raises:
        UserNotFoundException: If the user is not found.
    """
    query = select(UserModel).where(UserModel.email == email)
    result = (await db.execute(query)).scalar_one_or_none()
    if result is None:
        raise UserNotFoundException
    return result


async def get_user_model_by_id(db: AsyncSession, *, user_id: int) -> UserModel:
    """Retrieve a user model by user ID.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        user_id (int): User ID.

    Returns:
        UserModel: The user model.

    Raises:
        UserNotFoundException: If the user is not found.
    """
    query = select(UserModel).where(UserModel.id == user_id)
    result = (await db.execute(query)).scalar_one_or_none()
    if result is None:
        raise UserNotFoundException
    return result


async def get_user(db: AsyncSession, *, user_id: int) -> UserSchema:
    """Retrieve a user schema by user ID.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        user_id (int): User ID.

    Returns:
        UserSchema: The user schema.
    """
    user_model = await get_user_model_by_id(db, user_id=user_id)
    return UserSchema.model_construct(**user_model.to_dict())


async def update_user(db: AsyncSession, *, user_id: int, schema: UserUpdateSchema | UserPatchSchema) -> UserSchema:
    """Update an existing user in the database.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        user_id (int): User ID to update.
        schema (UserUpdateSchema | UserPatchSchema): Schema containing updated user data.

    Returns:
        UserSchema: The updated user schema.
    """
    user_model = await get_user_model_by_id(db, user_id=user_id)

    if schema.email and schema.email != user_model.email:
        await raise_for_user_email(db, schema.email)

    for field, value in schema.iterate_set_fields():
        setattr(user_model, field, value)

    await db.flush()
    return UserSchema.model_construct(**user_model.to_dict())


async def delete_user(db: AsyncSession, *, user_id: int) -> None:
    """Delete a user by marking them as deleted.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        user_id (int): User ID to delete.
    """
    user_model = await get_user_model_by_id(db, user_id=user_id)
    user_model.deleted_at = datetime.now(timezone.utc)

    await db.flush()


async def get_expiry_users(db: AsyncSession) -> Sequence[tuple[UserModel, int]]:
    query = (
        select(
            UserModel,
            func.extract(
                "day",
                func.min((ProductModel.manufactured_at + ProductTypeModel.exp_period_before_opening) - func.now()),
            ).label("days"),
        )
        .join(ProductModel, ProductModel.owner_id == UserModel.id)
        .join(FridgeProductModel, FridgeProductModel.product_id == ProductModel.id)
        .join(ProductTypeModel, ProductTypeModel.id == ProductModel.product_type_id)
        .where(UserModel.tg_id.is_not(None), FridgeProductModel.deleted_at.is_(None))
    ).group_by(UserModel.id)

    res = (await db.execute(query)).all()
    return res  # type: ignore
