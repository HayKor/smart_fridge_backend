from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_fridge.core.exceptions.product import ProductForbiddenException, ProductNotFoundException
from smart_fridge.lib.models import ProductModel
from smart_fridge.lib.schemas.product import ProductCreateSchema, ProductPatchSchema, ProductSchema, ProductUpdateSchema


def _raise_for_user_access(product_model: ProductModel, user_id: int) -> None:
    """Raise an exception if the user does not have access to the product.

    Args:
        product_model (ProductModel): The product model to check access for.
        user_id (int): The ID of the user.
    """
    if not product_model.owner_id == user_id:
        raise ProductForbiddenException


async def create_product(db: AsyncSession, user_id: int, schema: ProductCreateSchema) -> ProductSchema:
    """Create a new product in the database.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        user_id (int): The ID of the user creating the product.
        schema (ProductCreateSchema): The schema containing product data.

    Returns:
        ProductSchema: The created product schema.
    """
    product_model = ProductModel(**schema.model_dump(), owner_id=user_id)
    db.add(product_model)
    await db.flush()
    return ProductSchema.model_construct(**product_model.to_dict())


async def get_products(db: AsyncSession, user_id: int) -> list[ProductSchema]:
    """Retrieve all products owned by the user.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        user_id (int): The ID of the user.

    Returns:
        list[ProductSchema]: A list of product schemas owned by the user.
    """
    query = select(ProductModel).where(ProductModel.owner_id == user_id)
    products = (await db.execute(query)).scalars().all()

    items = [ProductSchema.model_construct(**i.to_dict()) for i in products]
    return items


async def get_product(db: AsyncSession, product_id: int, user_id: int) -> ProductSchema:
    """Retrieve a specific product by its ID.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        product_id (int): The ID of the product to retrieve.
        user_id (int): The ID of the user requesting the product.

    Returns:
        ProductSchema: The product schema.
    """
    product_model = await get_product_model(db, product_id=product_id)
    _raise_for_user_access(product_model, user_id)
    return ProductSchema.model_construct(**product_model.to_dict())


async def update_product(
    db: AsyncSession, product_id: int, schema: ProductUpdateSchema | ProductPatchSchema, user_id: int
) -> ProductSchema:
    """Update an existing product with new data.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        product_id (int): The ID of the product to update.
        schema (ProductUpdateSchema | ProductPatchSchema): The schema containing updated product data.
        user_id (int): The ID of the user updating the product.

    Returns:
        ProductSchema: The updated product schema.
    """
    product_model = await get_product_model(db, product_id=product_id)
    _raise_for_user_access(product_model, user_id)

    for field, value in schema.iterate_set_fields():
        setattr(product_model, field, value)

    await db.flush()
    return ProductSchema.model_construct(**product_model.to_dict())


async def set_product_opened(db: AsyncSession, product_id: int, user_id: int) -> ProductSchema:
    """Set a product's status to opened.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        product_id (int): The ID of the product to update.
        user_id (int): The ID of the user updating the product.

    Returns:
        ProductSchema: The updated product schema.
    """
    schema = ProductPatchSchema.model_construct(opened_at=datetime.now(timezone.utc))
    return await update_product(db, product_id, schema, user_id)


async def set_product_closed(db: AsyncSession, product_id: int, user_id: int) -> ProductSchema:
    """Set a product's status to closed.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        product_id (int): The ID of the product to update.
        user_id (int): The ID of the user updating the product.

    Returns:
        ProductSchema: The updated product schema.
    """
    schema = ProductPatchSchema.model_construct(opened_at=None)
    return await update_product(db, product_id, schema, user_id)


async def delete_product(db: AsyncSession, product_id: int, user_id: int) -> None:
    """Delete a product from the database.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        product_id (int): The ID of the product to delete.
        user_id (int): The ID of the user requesting the deletion.
    """
    product_model = await get_product_model(db, product_id)
    _raise_for_user_access(product_model, user_id)
    await db.delete(product_model)
    await db.flush()


async def get_product_model(db: AsyncSession, product_id: int) -> ProductModel:
    """Retrieve a product model by its ID.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        product_id (int): The ID of the product to retrieve.

    Returns:
        ProductModel: The product model.
    """
    query = select(ProductModel).where(ProductModel.id == product_id)
    result = (await db.execute(query)).scalar_one_or_none()
    if result is None:
        raise ProductNotFoundException
    return result
