from datetime import datetime

from .abc import BaseSchema


class BaseProductSchema(BaseSchema):
    amount: int


class ProductCreateSchema(BaseProductSchema):
    product_type_id: int
    owner_id: int
    manufacture_at: datetime | None = None


class ProductUpdateSchema(ProductCreateSchema):
    pass


class ProductPatchSchema(BaseSchema):
    amount: int | None = None
    manufacture_at: datetime | None = None
    opened_at: datetime | None


class ProductSchema(ProductCreateSchema):
    id: int
    opened_at: datetime | None = None
