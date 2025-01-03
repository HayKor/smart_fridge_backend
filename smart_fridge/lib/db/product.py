from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_fridge.core.exceptions.product import ProductNotFoundException
from smart_fridge.lib.models import ProductModel
from smart_fridge.lib.schemas.product import ProductCreateSchema, ProductPatchSchema, ProductSchema, ProductUpdateSchema


async def create_product(
    db: AsyncSession,
    user_id: int,
    schema: ProductCreateSchema,
) -> ProductSchema:
    product_model = ProductModel(**schema.model_dump(exclude={"owner_id"}), owner_id=user_id)
    db.add(product_model)
    await db.flush()
    return ProductSchema.model_construct(**product_model.to_dict())


async def get_products(db: AsyncSession, user_id: int) -> list[ProductSchema]:
    query = select(ProductModel).where(ProductModel.owner_id == user_id)
    products = (await db.execute(query)).scalars().all()

    items = [ProductSchema.model_construct(**i.to_dict()) for i in products]
    return items


async def get_product(
    db: AsyncSession,
    product_id: int,
) -> ProductSchema:
    product_model = await get_product_model(db, product_id=product_id)
    return ProductSchema.model_construct(**product_model.to_dict())


async def update_product(
    db: AsyncSession,
    product_id: int,
    schema: ProductUpdateSchema | ProductPatchSchema,
):
    product_model = await get_product_model(db, product_id=product_id)

    for field, value in schema.iterate_set_fields():
        setattr(product_model, field, value)

    await db.flush()
    return ProductSchema.model_construct(**product_model.to_dict())


async def set_product_opened(
    db: AsyncSession,
    product_id: int,
):
    product_model = await get_product_model(db, product_id=product_id)
    product_model.opened_at = datetime.now(timezone.utc)

    await db.flush()
    return ProductSchema.model_construct(**product_model.to_dict())


async def delete_product(
    db: AsyncSession,
    product_id: int,
) -> None:
    product_model = await get_product_model(db, product_id)
    await db.delete(product_model)
    await db.flush()


async def get_product_model(
    db: AsyncSession,
    product_id: int,
) -> ProductModel:
    query = select(ProductModel).where(ProductModel.id == product_id)
    result = (await db.execute(query)).scalar_one_or_none()
    if result is None:
        raise ProductNotFoundException
    return result
