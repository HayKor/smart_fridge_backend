from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from smart_fridge.core.exceptions.cart_product import CartProductForbiddenException, CartProductNotFoundException
from smart_fridge.lib.models import CartProductModel
from smart_fridge.lib.schemas.cart_product import (
    CartProductCreateSchema,
    CartProductPatchSchema,
    CartProductSchema,
    CartProductUpdateSchema,
)


def _raise_for_user_access(cart_product_model: CartProductModel, user_id: int) -> None:
    if not cart_product_model.owner_id == user_id:
        raise CartProductForbiddenException


async def create_cart_product(db: AsyncSession, user_id: int, schema: CartProductCreateSchema) -> CartProductSchema:
    cart_product_model = CartProductModel(**schema.model_dump(), owner_id=user_id)
    db.add(cart_product_model)
    await db.flush()
    return CartProductSchema.model_construct(**cart_product_model.to_dict())


async def get_cart_products(db: AsyncSession, user_id: int) -> list[CartProductSchema]:
    query = (
        select(CartProductModel)
        .where(CartProductModel.owner_id == user_id, CartProductModel.deleted_at.is_(None))
        .options(joinedload(CartProductModel.product_type))
    )
    cart_products = (await db.execute(query)).scalars().all()

    items = [CartProductSchema.model_construct(**i.to_dict()) for i in cart_products]
    return items


async def get_cart_product(db: AsyncSession, cart_product_id: int, user_id: int) -> CartProductSchema:
    cart_product_model = await get_cart_product_model(db, cart_product_id=cart_product_id, join_product_type=True)
    _raise_for_user_access(cart_product_model, user_id)
    return CartProductSchema.model_validate(cart_product_model.to_dict())


async def get_cart_product_model(
    db: AsyncSession, cart_product_id: int, join_product_type: bool = False
) -> CartProductModel:
    query = select(CartProductModel).where(CartProductModel.id == cart_product_id)
    if join_product_type:
        query = query.options(joinedload(CartProductModel.product_type))
    result = (await db.execute(query)).scalar_one_or_none()
    if result is None:
        raise CartProductNotFoundException
    return result


async def update_cart_product(
    db: AsyncSession, cart_product_id: int, schema: CartProductUpdateSchema | CartProductPatchSchema, user_id: int
) -> CartProductSchema:
    cart_product_model = await get_cart_product_model(db, cart_product_id=cart_product_id)
    _raise_for_user_access(cart_product_model, user_id)

    for field, value in schema.iterate_set_fields():
        setattr(cart_product_model, field, value)

    await db.flush()
    return CartProductSchema.model_construct(**cart_product_model.to_dict())


async def delete_cart_product(db: AsyncSession, cart_product_id: int, user_id: int) -> None:
    cart_product_model = await get_cart_product_model(db, cart_product_id)
    _raise_for_user_access(cart_product_model, user_id)
    cart_product_model.deleted_at = datetime.now(timezone.utc)
    await db.flush()
