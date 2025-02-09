from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from smart_fridge.core.exceptions.fridge_product import (
    FridgeProductForbiddenException,
    FridgeProductlAlreadyExistsException,
    FridgeProductNotFoundException,
)
from smart_fridge.lib.models import FridgeProductModel
from smart_fridge.lib.models.product import ProductModel
from smart_fridge.lib.schemas.fridge_product import (
    FridgeProductCreateSchema,
    FridgeProductFilterSchema,
    FridgeProductPaginationResponse,
    FridgeProductPatchSchema,
    FridgeProductSchema,
    FridgeProductUpdateSchema,
)
from smart_fridge.lib.schemas.pagination import PaginationRequest
from smart_fridge.lib.utils.filter import add_filters_to_query
from smart_fridge.lib.utils.pagination import add_pagination_to_query, get_rows_count_in


async def create_fridge_product(db: AsyncSession, schema: FridgeProductCreateSchema) -> FridgeProductSchema:
    """Create a new fridge product in the database.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        schema (FridgeProductCreateSchema): Schema containing product details.

    Returns:
        FridgeProductSchema: The created fridge product schema.
    """
    await raise_for_product(db, schema.product_id)

    fridge_product_model = FridgeProductModel(**schema.model_dump())
    db.add(fridge_product_model)
    await db.flush()
    return FridgeProductSchema.model_construct(**fridge_product_model.to_dict())


async def get_fridge_product(db: AsyncSession, fridge_product_id: int, user_id: int) -> FridgeProductSchema:
    """Retrieve a specific fridge product by its ID for a given user.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        fridge_product_id (int): ID of the fridge product to retrieve.
        user_id (int): ID of the user requesting the product.

    Returns:
        FridgeProductSchema: The retrieved fridge product schema.
    """
    fridge_product_model = await get_fridge_product_model(
        db, fridge_product_id=fridge_product_id, join_product=True, join_product_type=True
    )
    _raise_for_user_access(fridge_product_model, user_id)
    return FridgeProductSchema.model_construct(**fridge_product_model.to_dict())


async def get_fridge_products(
    db: AsyncSession,
    filters: FridgeProductFilterSchema,
    pagination: PaginationRequest,
    user_id: int,
) -> FridgeProductPaginationResponse:
    """Retrieve a list of fridge products for a user with optional filters and pagination.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        filters (FridgeProductFilterSchema): Filters to apply to the product query.
        pagination (PaginationRequest): Pagination details for the query.
        user_id (int): ID of the user requesting the products.

    Returns:
        FridgeProductPaginationResponse: A response containing the list of fridge products and pagination info.
    """
    query_filter = (
        ProductModel.owner_id == user_id,
        FridgeProductModel.deleted_at.is_(None),
    )

    subquery = select(FridgeProductModel.id).where(*query_filter).group_by(FridgeProductModel.id)
    query = (
        select(FridgeProductModel)
        .options(
            selectinload(FridgeProductModel.product),
            selectinload(FridgeProductModel.product).selectinload(ProductModel.product_type),
        )
        .where(FridgeProductModel.id.in_(subquery))
    )
    query_count = select(func.count(FridgeProductModel.id)).where(FridgeProductModel.id.in_(subquery))

    query = add_filters_to_query(query, FridgeProductModel, filters)
    query_count = add_filters_to_query(query_count, FridgeProductModel, filters, include_order_by=False)
    query = add_pagination_to_query(query, pagination)

    fridge_products = (await db.execute(query)).scalars().all()
    schemas = [FridgeProductSchema.model_validate(i.to_dict()) for i in fridge_products]

    count, pages = await get_rows_count_in(db, query_count, pagination.limit)
    return FridgeProductPaginationResponse.model_construct(items=schemas, total_items=count, total_pages=pages)


async def update_fridge_product(
    db: AsyncSession, fridge_product_id: int, schema: FridgeProductUpdateSchema | FridgeProductPatchSchema, user_id: int
) -> FridgeProductSchema:
    """Update an existing fridge product for a given user.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        fridge_product_id (int): ID of the fridge product to update.
        schema (FridgeProductUpdateSchema | FridgeProductPatchSchema): Schema containing updated product details.
        user_id (int): ID of the user requesting the update.

    Returns:
        FridgeProductSchema: The updated fridge product schema.
    """
    fridge_product_model = await get_fridge_product_model(db, fridge_product_id=fridge_product_id)
    _raise_for_user_access(fridge_product_model, user_id)

    for field, value in schema.iterate_set_fields():
        setattr(fridge_product_model, field, value)

    await db.flush()
    return FridgeProductSchema.model_construct(**fridge_product_model.to_dict())


async def delete_fridge_product(db: AsyncSession, fridge_product_id: int, user_id: int) -> None:
    """Delete a fridge product by marking it as deleted for a given user.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        fridge_product_id (int): ID of the fridge product to delete.
        user_id (int): ID of the user requesting the deletion.
    """
    fridge_product_model = await get_fridge_product_model(db, fridge_product_id, join_product=True)
    _raise_for_user_access(fridge_product_model, user_id)
    fridge_product_model.deleted_at = datetime.now(timezone.utc)
    await db.flush()


async def get_fridge_product_model(
    db: AsyncSession, fridge_product_id: int, join_product: bool = False, join_product_type: bool = False
) -> FridgeProductModel:
    """Retrieve a fridge product model from the database by its ID, with optional joins.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        fridge_product_id (int): ID of the fridge product to retrieve.
        join_product (bool): Whether to join the product details.
        join_product_type (bool): Whether to join the product type details.

    Returns:
        FridgeProductModel: The retrieved fridge product model.

    Raises:
        FridgeProductNotFoundException: If the fridge product is not found.
    """
    query = select(FridgeProductModel).where(FridgeProductModel.id == fridge_product_id)
    if join_product:
        join_options = [joinedload(FridgeProductModel.product)]
        if join_product_type:
            join_options.append(joinedload(FridgeProductModel.product).joinedload(ProductModel.product_type))
        query = query.options(*join_options)

    result = (await db.execute(query)).scalar_one_or_none()
    if result is None:
        raise FridgeProductNotFoundException
    return result


async def is_product_exists(db: AsyncSession, product_id: int) -> bool:
    """Check if a product exists in the fridge products.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        product_id (int): ID of the product to check.

    Returns:
        bool: True if the product exists, False otherwise.
    """
    query = select(FridgeProductModel).where(FridgeProductModel.product_id == product_id)
    return bool((await db.execute(query)).scalar_one_or_none())


async def raise_for_product(db: AsyncSession, product_id: int) -> None:
    """Raise an exception if the product already exists in the fridge products.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        product_id (int): ID of the product to check.

    Raises:
        FridgeProductlAlreadyExistsException: If the product already exists.
    """
    if await is_product_exists(db, product_id):
        raise FridgeProductlAlreadyExistsException(product_id=product_id)


def _raise_for_user_access(fridge_product_model: FridgeProductModel, user_id: int) -> None:
    """Check if the user has access to the specified fridge product.

    Args:
        fridge_product_model (FridgeProductModel): The fridge product model to check access for.
        user_id (int): ID of the user to check access for.

    Raises:
        FridgeProductForbiddenException: If the user does not have access.
    """
    if not fridge_product_model.product.owner_id == user_id:
        raise FridgeProductForbiddenException
