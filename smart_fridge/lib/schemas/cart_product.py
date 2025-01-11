from datetime import datetime

from . import fields as f
from .abc import BaseSchema
from .pagination import PaginationResponse
from .product_type import PRODUCT_TYPE_ID
from .user import USER_ID


CART_PRODUCT_ID = f.ID(description="Cart product ID.")
CREATED_AT = f.DATETIME(description="Cart product creation datetime")
DELETED_AT = f.DATETIME(description="Cart product deletion datetime")


class BaseCartProductSchema(BaseSchema):
    pass


class CartProductCreateSchema(BaseCartProductSchema):
    product_type_id: int = PRODUCT_TYPE_ID


class CartProductUpdateSchema(BaseCartProductSchema):
    pass


class CartProductPatchSchema(BaseCartProductSchema):
    deleted_at: datetime | None = DELETED_AT(default=None)


class CartProductSchema(BaseCartProductSchema):
    id: int = CART_PRODUCT_ID
    owner_id: int = USER_ID
    created_at: datetime = CREATED_AT
    deleted_at: datetime | None = DELETED_AT(default=None)


class CartProductPaginationResponse(PaginationResponse[CartProductSchema]):
    pass
