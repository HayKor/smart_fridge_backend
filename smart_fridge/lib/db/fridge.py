from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from smart_fridge.core.exceptions.fridge import FridgeForbiddenException, FridgeNotFoundException
from smart_fridge.lib.models import FridgeModel
from smart_fridge.lib.schemas.fridge import FridgeCreateSchema, FridgePatchSchema, FridgeSchema, FridgeUpdateSchema


def _raise_for_user_access(fridge_model: FridgeModel, user_id: int) -> None:
    if not fridge_model.owner_id == user_id:
        raise FridgeForbiddenException


async def create_fridge(db: AsyncSession, user_id: int, schema: FridgeCreateSchema) -> FridgeSchema:
    fridge_model = FridgeModel(**schema.model_dump(), owner_id=user_id)
    db.add(fridge_model)
    await db.flush()
    return FridgeSchema.model_construct(**fridge_model.to_dict())


async def get_fridges(db: AsyncSession, user_id: int) -> list[FridgeSchema]:
    query = select(FridgeModel).where(FridgeModel.owner_id == user_id)
    fridges = (await db.execute(query)).scalars().all()

    items = [FridgeSchema.model_construct(**i.to_dict()) for i in fridges]
    return items


async def get_fridge(db: AsyncSession, fridge_id: int, user_id: int) -> FridgeSchema:
    fridge_model = await get_fridge_model(db, fridge_id=fridge_id, join_products=True)
    _raise_for_user_access(fridge_model, user_id)
    return FridgeSchema.model_validate(fridge_model.to_dict())


async def update_fridge(
    db: AsyncSession, fridge_id: int, schema: FridgeUpdateSchema | FridgePatchSchema, user_id: int
) -> FridgeSchema:
    fridge_model = await get_fridge_model(db, fridge_id=fridge_id)
    _raise_for_user_access(fridge_model, user_id)

    for field, value in schema.iterate_set_fields():
        setattr(fridge_model, field, value)

    await db.flush()
    return FridgeSchema.model_construct(**fridge_model.to_dict())


async def delete_fridge(db: AsyncSession, fridge_id: int, user_id: int) -> None:
    fridge_model = await get_fridge_model(db, fridge_id)
    _raise_for_user_access(fridge_model, user_id)
    await db.delete(fridge_model)
    await db.flush()


async def get_fridge_model(db: AsyncSession, fridge_id: int, join_products: bool = False) -> FridgeModel:
    query = select(FridgeModel).where(FridgeModel.id == fridge_id)
    if join_products:
        query = query.options(joinedload(FridgeModel.fridge_products))
    result = (await db.execute(query)).unique().scalar_one_or_none()
    if result is None:
        raise FridgeNotFoundException
    return result
