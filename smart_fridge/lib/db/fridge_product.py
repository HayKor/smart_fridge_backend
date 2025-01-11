from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

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
    await raise_for_product(db, schema.product_id)

    fridge_product_model = FridgeProductModel(**schema.model_dump())
    db.add(fridge_product_model)
    await db.flush()
    return FridgeProductSchema.model_construct(**fridge_product_model.to_dict())


async def get_fridge_product(db: AsyncSession, fridge_product_id: int, user_id: int) -> FridgeProductSchema:
    fridge_product_model = await get_fridge_product_model(db, fridge_product_id=fridge_product_id, join_product=True)
    _raise_for_user_access(fridge_product_model, user_id)
    return FridgeProductSchema.model_construct(**fridge_product_model.to_dict())


async def get_fridge_products(
    db: AsyncSession,
    filters: FridgeProductFilterSchema,
    pagination: PaginationRequest,
    user_id: int,
) -> FridgeProductPaginationResponse:
    query = (
        select(FridgeProductModel)
        .options(joinedload(FridgeProductModel.product).joinedload(ProductModel.product_type))
        .where(ProductModel.owner_id == user_id, FridgeProductModel.deleted_at.is_(None))
    )
    query_count = select(func.count(FridgeProductModel.id))

    query = add_filters_to_query(query, FridgeProductModel, filters)
    query_count = add_filters_to_query(query_count, FridgeProductModel, filters, include_order_by=False)
    query = add_pagination_to_query(query, pagination)

    fridge_products: Sequence[FridgeProductModel] = (await db.execute(query)).scalars().all()
    schemas = [FridgeProductSchema.model_validate(i.to_dict()) for i in fridge_products]

    count, pages = await get_rows_count_in(db, query_count, pagination.limit)
    return FridgeProductPaginationResponse.model_construct(items=schemas, total_items=count, total_pages=pages)


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


async def is_product_exists(db: AsyncSession, product_id: int) -> bool:
    query = select(FridgeProductModel).where(FridgeProductModel.product_id == product_id)
    return bool((await db.execute(query)).scalar_one_or_none())


async def raise_for_product(db: AsyncSession, product_id: int) -> None:
    if await is_product_exists(db, product_id):
        raise FridgeProductlAlreadyExistsException(product_id=product_id)


def _raise_for_user_access(fridge_product_model: FridgeProductModel, user_id: int) -> None:
    if not fridge_product_model.product.owner_id == user_id:
        raise FridgeProductForbiddenException
