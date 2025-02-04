from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import count

from smart_fridge.lib.models.fridge_product import FridgeProductModel
from smart_fridge.lib.models.product import ProductModel
from smart_fridge.lib.models.product_type import ProductTypeModel
from smart_fridge.lib.schemas.statistics import StatisticsFilterSchema, StatisticsSchema, StatisticsUnitSchema


async def get_stats(db: AsyncSession, user_id: int, filter: StatisticsFilterSchema) -> StatisticsSchema:
    added = await get_added(db, user_id, filter)
    deleted = await get_deleted(db, user_id, filter)
    exceeded = await get_exceeded(db, user_id, filter)
    return StatisticsSchema(added=added, deleted=deleted, exceeded=exceeded)


async def get_added(db: AsyncSession, user_id: int, filter: StatisticsFilterSchema) -> list[StatisticsUnitSchema]:
    query = (
        select(ProductTypeModel, count(ProductTypeModel.id).label("amount"))
        .join(ProductModel, ProductModel.product_type_id == ProductTypeModel.id)
        .join(FridgeProductModel, FridgeProductModel.product_id == ProductModel.id)
        .where(ProductModel.owner_id == user_id)
        .filter(FridgeProductModel.created_at >= filter.date_from, FridgeProductModel.created_at <= filter.date_to)
        .group_by(ProductTypeModel.id)
    )

    stats = (await db.execute(query)).all()
    return [StatisticsUnitSchema(product_type=pt, amount=amount) for pt, amount in stats]


async def get_deleted(db: AsyncSession, user_id: int, filter: StatisticsFilterSchema) -> list[StatisticsUnitSchema]:
    query = (
        select(ProductTypeModel, count(ProductTypeModel.id).label("amount"))
        .join(ProductModel, ProductModel.product_type_id == ProductTypeModel.id)
        .join(FridgeProductModel, FridgeProductModel.product_id == ProductModel.id)
        .where(ProductModel.owner_id == user_id, FridgeProductModel.deleted_at.is_not(None))
        .filter(FridgeProductModel.deleted_at >= filter.date_from, FridgeProductModel.deleted_at <= filter.date_to)
        .group_by(ProductTypeModel.id)
    )

    stats = (await db.execute(query)).all()
    return [StatisticsUnitSchema(product_type=pt, amount=amount) for pt, amount in stats]


async def get_exceeded(db: AsyncSession, user_id: int, filter: StatisticsFilterSchema) -> list[StatisticsUnitSchema]:
    query = (
        select(ProductTypeModel, count("*").label("amount"))
        .join(ProductModel, ProductModel.product_type_id == ProductTypeModel.id)
        .join(FridgeProductModel, FridgeProductModel.product_id == ProductModel.id)
        .where(
            or_(
                and_(
                    FridgeProductModel.deleted_at.is_(None),
                    (ProductModel.manufactured_at + ProductTypeModel.exp_period_before_opening).between(
                        filter.date_from, func.now()
                    ),
                ),
                and_(
                    FridgeProductModel.deleted_at.is_not(None),
                    (ProductModel.manufactured_at + ProductTypeModel.exp_period_before_opening).between(
                        filter.date_from, filter.date_to
                    ),
                ),
            ),
            ProductModel.owner_id == user_id,
        )
    ).group_by(ProductTypeModel.id)

    stats = (await db.execute(query)).all()
    return [StatisticsUnitSchema(product_type=pt, amount=amount) for pt, amount in stats]
