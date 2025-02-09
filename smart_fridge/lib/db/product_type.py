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
    """Create a new product type in the database.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        schema (ProductTypeCreateSchema): Schema containing product type data.

    Returns:
        ProductTypeSchema: The created product type.
    """
    product_type_model = ProductTypeModel(**schema.model_dump())
    db.add(product_type_model)
    await db.flush()
    return ProductTypeSchema.model_construct(**product_type_model.to_dict())


async def get_product_types(db: AsyncSession) -> list[ProductTypeSchema]:
    """Retrieve all product types from the database.

    Args:
        db (AsyncSession): Async SQLAlchemy session.

    Returns:
        list[ProductTypeSchema]: A list of all product types.
    """
    query = select(ProductTypeModel)
    product_types = (await db.execute(query)).scalars().all()

    items = [ProductTypeSchema.model_construct(**i.to_dict()) for i in product_types]
    return items


async def get_product_type(db: AsyncSession, product_type_id: int) -> ProductTypeSchema:
    """Retrieve a specific product type by its ID.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        product_type_id (int): The ID of the product type to retrieve.

    Returns:
        ProductTypeSchema: The requested product type.
    """
    product_type_model = await get_product_type_model(db, product_type_id=product_type_id)
    return ProductTypeSchema.model_construct(**product_type_model.to_dict())


async def update_product_type(
    db: AsyncSession, product_type_id: int, schema: ProductTypeUpdateSchema | ProductTypePatchSchema
) -> ProductTypeSchema:
    """Update an existing product type in the database.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        product_type_id (int): The ID of the product type to update.
        schema (ProductTypeUpdateSchema | ProductTypePatchSchema): Schema containing updated product type data.

    Returns:
        ProductTypeSchema: The updated product type.
    """
    product_type_model = await get_product_type_model(db, product_type_id=product_type_id)

    for field, value in schema.iterate_set_fields():
        setattr(product_type_model, field, value)

    await db.flush()
    return ProductTypeSchema.model_construct(**product_type_model.to_dict())


async def delete_product_type(db: AsyncSession, product_type_id: int) -> None:
    """Delete a product type from the database.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        product_type_id (int): The ID of the product type to delete.
    """
    product_type_model = await get_product_type_model(db, product_type_id)
    await db.delete(product_type_model)
    await db.flush()


async def get_product_type_model(db: AsyncSession, product_type_id: int) -> ProductTypeModel:
    """Retrieve the product type model by its ID.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        product_type_id (int): The ID of the product type to retrieve.

    Returns:
        ProductTypeModel: The requested product type model.

    Raises:
        ProductTypeNotFoundException: If the product type with the given ID does not exist.
    """
    query = select(ProductTypeModel).where(ProductTypeModel.id == product_type_id)
    result = (await db.execute(query)).scalar_one_or_none()
    if result is None:
        raise ProductTypeNotFoundException
    return result
