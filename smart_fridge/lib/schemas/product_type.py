from datetime import timedelta

from smart_fridge.lib.models.product_type import AccountType

from .abc import BaseSchema


class BaseProductTypeSchema(BaseSchema):
    name: str
    slug: str
    account_type: AccountType


class ProductTypeCreateSchema(BaseProductTypeSchema):
    exp_period_before_opening: timedelta
    exp_period_after_opening: timedelta | None = None
    calories: int | None = None


class ProductTypeUpdateSchema(ProductTypeCreateSchema):
    pass


class ProductTypePatchSchema(BaseSchema):
    name: str | None = None
    slug: str | None = None
    exp_period_before_opening: timedelta | None = None
    exp_period_after_opening: timedelta | None = None
    calories: int | None = None


class ProductTypeSchema(ProductTypeCreateSchema):
    id: int
