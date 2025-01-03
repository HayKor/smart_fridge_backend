from datetime import timedelta

from smart_fridge.lib.models.product_type import AccountType

from . import fields as f
from .abc import BaseSchema


PRODUCT_TYPE_ID = f.ID(prefix="Product type ID.")
PRODUCT_TYPE_NAME = f.BaseField(description="Product type name", examples=["Хлеб белый 'Чистая линия'"])
PRODUCT_TYPE_SLUG = f.BaseField(description="Product type slug", examples=["Хлеб"])
PRODUCT_TYPE_CALORIES = f.BaseField(default=None, description="Product type calories per 100g", examples=[100], ge=0)
EXP_PERIOD_BEFORE_OPENING = f.BaseField(description="Product type expiration period before opening", examples=["P3D"])
EXP_PERIOD_AFTER_OPENING = f.BaseField(
    default=None, description="Product type expiration period after opening", examples=["P3D"]
)
ACCOUNT_TYPE = f.BaseField(description="Product type account type", examples=["weight"])


class BaseProductTypeSchema(BaseSchema):
    name: str = PRODUCT_TYPE_NAME
    slug: str = PRODUCT_TYPE_SLUG
    account_type: AccountType = ACCOUNT_TYPE


class ProductTypeCreateSchema(BaseProductTypeSchema):
    exp_period_before_opening: timedelta = EXP_PERIOD_BEFORE_OPENING
    exp_period_after_opening: timedelta | None = EXP_PERIOD_AFTER_OPENING
    calories: int | None = PRODUCT_TYPE_CALORIES


class ProductTypeUpdateSchema(ProductTypeCreateSchema):
    pass


class ProductTypePatchSchema(ProductTypeCreateSchema):
    name: str = PRODUCT_TYPE_NAME(default=None)
    slug: str = PRODUCT_TYPE_SLUG(default=None)
    account_type: AccountType = ACCOUNT_TYPE(default=None)
    exp_period_before_opening: timedelta = EXP_PERIOD_BEFORE_OPENING(default=None)
    exp_period_after_opening: timedelta | None = EXP_PERIOD_AFTER_OPENING(default=None)
    calories: int | None = PRODUCT_TYPE_CALORIES(default=None)


class ProductTypeSchema(ProductTypeCreateSchema):
    id: int = PRODUCT_TYPE_ID
