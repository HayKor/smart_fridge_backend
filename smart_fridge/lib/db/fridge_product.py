from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from smart_fridge.core.exceptions.fridge_product import FridgeProductForbiddenException, FridgeProductNotFoundException
from smart_fridge.lib.models import FridgeProductModel
from smart_fridge.lib.schemas.fridge_product import (
    FridgeProductCreateSchema,
    FridgeProductPatchSchema,
    FridgeProductSchema,
    FridgeProductUpdateSchema,
)


def _raise_for_user_access(fridge_product_model: FridgeProductModel, user_id: int) -> None:
    if not fridge_product_model.product.owner_id == user_id:
        raise FridgeProductForbiddenException


async def create_fridge_product(db: AsyncSession, schema: FridgeProductCreateSchema) -> FridgeProductSchema:
    fridge_product_model = FridgeProductModel(**schema.model_dump())
    db.add(fridge_product_model)
    await db.flush()
    return FridgeProductSchema.model_construct(**fridge_product_model.to_dict())


async def get_fridge_product(db: AsyncSession, fridge_product_id: int, user_id: int) -> FridgeProductSchema:
    fridge_product_model = await get_fridge_product_model(db, fridge_product_id=fridge_product_id, join_product=True)
    _raise_for_user_access(fridge_product_model, user_id)
    return FridgeProductSchema.model_construct(**fridge_product_model.to_dict())


async def update_fridge_product(
    db: AsyncSession, fridge_product_id: int, schema: FridgeProductUpdateSchema | FridgeProductPatchSchema, user_id: int
) -> FridgeProductSchema:
    fridge_product_model = await get_fridge_product_model(db, fridge_product_id=fridge_product_id, join_product=True)
    _raise_for_user_access(fridge_product_model, user_id)

    for field, value in schema.iterate_set_fields():
        setattr(fridge_product_model, field, value)

    await db.flush()
    return FridgeProductSchema.model_construct(**fridge_product_model.to_dict())


async def delete_fridge_product(db: AsyncSession, fridge_product_id: int, user_id: int) -> None:
    fridge_product_model = await get_fridge_product_model(db, fridge_product_id, join_product=True)
    _raise_for_user_access(fridge_product_model, user_id)
    fridge_product_model.deleted_at = datetime.now(timezone.utc)
    await db.flush()


async def get_fridge_product_model(
    db: AsyncSession, fridge_product_id: int, join_product: bool = False
) -> FridgeProductModel:
    query = select(FridgeProductModel).where(FridgeProductModel.id == fridge_product_id)
    if join_product:
        query = query.options(joinedload(FridgeProductModel.product))
    result = (await db.execute(query)).scalar_one_or_none()
    if result is None:
        raise FridgeProductNotFoundException
    return result
