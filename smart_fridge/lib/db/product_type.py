from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_fridge.core.exceptions.product_type import ProductTypeNotFoundException
from smart_fridge.lib.models import ProductTypeModel
from smart_fridge.lib.schemas.product_type import (
    ProductTypeCreateSchema,
    ProductTypePatchSchema,
    ProductTypeSchema,
    ProductTypeUpdateSchema,
)


async def create_product_type(db: AsyncSession, schema: ProductTypeCreateSchema) -> ProductTypeSchema:
    product_type_model = ProductTypeModel(**schema.model_dump())
    db.add(product_type_model)
    await db.flush()
    return ProductTypeSchema.model_construct(**product_type_model.to_dict())


async def get_product_types(db: AsyncSession) -> list[ProductTypeSchema]:
    query = select(ProductTypeModel)
    product_types = (await db.execute(query)).scalars().all()

    items = [ProductTypeSchema.model_construct(**i.to_dict()) for i in product_types]
    return items


async def get_product_type(db: AsyncSession, product_type_id: int) -> ProductTypeSchema:
    product_type_model = await get_product_type_model(db, product_type_id=product_type_id)
    return ProductTypeSchema.model_construct(**product_type_model.to_dict())


async def update_product_type(
    db: AsyncSession, product_type_id: int, schema: ProductTypeUpdateSchema | ProductTypePatchSchema
):
    product_type_model = await get_product_type_model(db, product_type_id=product_type_id)

    for field, value in schema.iterate_set_fields():
        setattr(product_type_model, field, value)

    await db.flush()
    return ProductTypeSchema.model_construct(**product_type_model.to_dict())


async def delete_product_type(db: AsyncSession, product_type_id: int) -> None:
    product_type_model = await get_product_type_model(db, product_type_id)
    await db.delete(product_type_model)
    await db.flush()


async def get_product_type_model(db: AsyncSession, product_type_id: int) -> ProductTypeModel:
    query = select(ProductTypeModel).where(ProductTypeModel.id == product_type_id)
    result = (await db.execute(query)).scalar_one_or_none()
    if result is None:
        raise ProductTypeNotFoundException
    return result
