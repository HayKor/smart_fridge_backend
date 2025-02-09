from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from smart_fridge.core.exceptions.fridge import FridgeForbiddenException, FridgeNotFoundException
from smart_fridge.lib.models import FridgeModel
from smart_fridge.lib.schemas.fridge import FridgeCreateSchema, FridgePatchSchema, FridgeSchema, FridgeUpdateSchema


def _raise_for_user_access(fridge_model: FridgeModel, user_id: int) -> None:
    """Check if the user has access to the specified fridge.

    Args:
        fridge_model (FridgeModel): The fridge model to check access for.
        user_id (int): The ID of the user.

    Raises:
        FridgeForbiddenException: If the user does not own the fridge.
    """
    if not fridge_model.owner_id == user_id:
        raise FridgeForbiddenException


async def create_fridge(db: AsyncSession, user_id: int, schema: FridgeCreateSchema) -> FridgeSchema:
    """Create a new fridge for the specified user.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        user_id (int): The ID of the user creating the fridge.
        schema (FridgeCreateSchema): The schema containing fridge data.

    Returns:
        FridgeSchema: The created fridge schema.
    """
    fridge_model = FridgeModel(**schema.model_dump(), owner_id=user_id)
    db.add(fridge_model)
    await db.flush()
    return FridgeSchema.model_construct(**fridge_model.to_dict())


async def get_fridges(db: AsyncSession, user_id: int) -> list[FridgeSchema]:
    """Retrieve all fridges owned by the specified user.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        user_id (int): The ID of the user.

    Returns:
        list[FridgeSchema]: A list of fridge schemas owned by the user.
    """
    query = select(FridgeModel).where(FridgeModel.owner_id == user_id)
    fridges = (await db.execute(query)).scalars().all()

    items = [FridgeSchema.model_construct(**i.to_dict()) for i in fridges]
    return items


async def get_fridge(db: AsyncSession, fridge_id: int, user_id: int) -> FridgeSchema:
    """Retrieve a specific fridge by its ID for the specified user.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        fridge_id (int): The ID of the fridge to retrieve.
        user_id (int): The ID of the user requesting the fridge.

    Returns:
        FridgeSchema: The requested fridge schema.

    Raises:
        FridgeForbiddenException: If the user does not own the fridge.
    """
    fridge_model = await get_fridge_model(db, fridge_id=fridge_id, join_products=True)
    _raise_for_user_access(fridge_model, user_id)
    return FridgeSchema.model_validate(fridge_model.to_dict())


async def update_fridge(
    db: AsyncSession, fridge_id: int, schema: FridgeUpdateSchema | FridgePatchSchema, user_id: int
) -> FridgeSchema:
    """Update an existing fridge with new data.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        fridge_id (int): The ID of the fridge to update.
        schema (FridgeUpdateSchema | FridgePatchSchema): The schema containing updated fridge data.
        user_id (int): The ID of the user updating the fridge.

    Returns:
        FridgeSchema: The updated fridge schema.

    Raises:
        FridgeForbiddenException: If the user does not own the fridge.
    """
    fridge_model = await get_fridge_model(db, fridge_id=fridge_id)
    _raise_for_user_access(fridge_model, user_id)

    for field, value in schema.iterate_set_fields():
        setattr(fridge_model, field, value)

    await db.flush()
    return FridgeSchema.model_construct(**fridge_model.to_dict())


async def delete_fridge(db: AsyncSession, fridge_id: int, user_id: int) -> None:
    """Delete a specific fridge owned by the user.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        fridge_id (int): The ID of the fridge to delete.
        user_id (int): The ID of the user requesting the deletion.

    Raises:
        FridgeForbiddenException: If the user does not own the fridge.
    """
    fridge_model = await get_fridge_model(db, fridge_id)
    _raise_for_user_access(fridge_model, user_id)
    await db.delete(fridge_model)
    await db.flush()


async def get_fridge_model(db: AsyncSession, fridge_id: int, join_products: bool = False) -> FridgeModel:
    """Retrieve the fridge model by its ID, optionally joining related products.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        fridge_id (int): The ID of the fridge to retrieve.
        join_products (bool): Whether to join related products in the query.

    Returns:
        FridgeModel: The retrieved fridge model.

    Raises:
        FridgeNotFoundException: If no fridge with the specified ID exists.
    """
    query = select(FridgeModel).where(FridgeModel.id == fridge_id)
    if join_products:
        query = query.options(joinedload(FridgeModel.fridge_products))
    result = (await db.execute(query)).unique().scalar_one_or_none()
    if result is None:
        raise FridgeNotFoundException
    return result
