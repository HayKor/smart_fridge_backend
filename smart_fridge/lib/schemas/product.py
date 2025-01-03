from datetime import datetime

from . import fields as f
from .abc import BaseSchema
from .product_type import PRODUCT_TYPE_ID


PRODUCT_ID = f.ID(prefix="Product ID.")
PRODUCT_AMOUNT = f.BaseField(description="Product amount based off of its accounting type", examples=[3])
MANUFACTURE_AT = f.DATETIME(description="Product manufacturing datetime")
OPENED_AT = f.DATETIME(description="Product opening datetime")


class BaseProductSchema(BaseSchema):
    amount: int = PRODUCT_AMOUNT


class ProductCreateSchema(BaseProductSchema):
    product_type_id: int = PRODUCT_TYPE_ID
    owner_id: int
    manufacture_at: datetime = MANUFACTURE_AT


class ProductUpdateSchema(ProductCreateSchema):
    pass


class ProductPatchSchema(ProductCreateSchema):
    amount: int = PRODUCT_AMOUNT(default=None)
    manufacture_at: datetime = MANUFACTURE_AT(default=None)
    opened_at: datetime | None = OPENED_AT(default=None)


class ProductSchema(ProductCreateSchema):
    id: int = PRODUCT_ID
    opened_at: datetime | None = OPENED_AT(default=None)
