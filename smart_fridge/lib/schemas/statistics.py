from datetime import datetime
from typing import Sequence

from smart_fridge.lib.schemas.product_type import ProductTypeSchema

from .abc import BaseSchema


class BaseStatistics(BaseSchema):
    pass


class StatisticsUnitSchema(BaseStatistics):
    product_type: ProductTypeSchema
    amount: int


class StatisticsSchema(BaseSchema):
    added: Sequence[StatisticsUnitSchema]
    deleted: Sequence[StatisticsUnitSchema]
    exceeded: Sequence[StatisticsUnitSchema]


class StatisticsFilterSchema(BaseSchema):
    date_from: datetime
    date_to: datetime
