from datetime import datetime

from . import fields as f
from .abc import BaseSchema
from .enums.filter import FilterType
from .fridge import FRIDGE_ID, FRIDGE_NAME
from .pagination import PaginationResponse
from .product import PRODUCT_ID
from .product_type import PRODUCT_TYPE_NAME


FRIDGE_PRODUCT_ID = f.ID(description="Fridge product ID.")
CREATED_AT = f.DATETIME(description="Fridge product creation datetime")
DELETED_AT = f.DATETIME(description="Fridge product deletion datetime")


class BaseFridgeProductSchema(BaseSchema):
    pass


class FridgeProductCreateSchema(BaseFridgeProductSchema):
    product_id: int = PRODUCT_ID
    fridge_id: int = FRIDGE_ID


class FridgeProductUpdateSchema(BaseFridgeProductSchema):
    pass


class FridgeProductPatchSchema(FridgeProductUpdateSchema):
    deleted_at: datetime | None = DELETED_AT(default=None)


class FridgeProductFilterSchema(BaseSchema):
    fridge_id_eq: int | None = FRIDGE_ID(default=None, filter_type=FilterType.eq, table_column="fridge_id")
    fridge_name_ilike: str | None = FRIDGE_NAME(default=None, filter_type=FilterType.ilike, table_column="fridge.name")
    product_name_ilike: str | None = PRODUCT_TYPE_NAME(
        default=None, filter_type=FilterType.ilike, table_column="product.product_type.name"
    )


class FridgeProductSchema(FridgeProductCreateSchema):
    id: int = FRIDGE_PRODUCT_ID
    created_at: datetime = CREATED_AT
    deleted_at: datetime | None = DELETED_AT(default=None)


class FridgeProductPaginationResponse(PaginationResponse[FridgeProductSchema]):
    pass
