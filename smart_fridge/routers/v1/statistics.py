from fastapi import APIRouter, Depends

from smart_fridge.core.dependencies.fastapi import DatabaseDependency, TokenDataDependency
from smart_fridge.lib.db import statistics as statistics_db
from smart_fridge.lib.schemas.statistics import StatisticsFilterSchema, StatisticsSchema


router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.get("/", response_model=StatisticsSchema)
async def get_stats(
    db: DatabaseDependency, token: TokenDataDependency, filter: StatisticsFilterSchema = Depends()
) -> StatisticsSchema:
    return await statistics_db.get_stats(db, token.user_id, filter)
