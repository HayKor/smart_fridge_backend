from datetime import datetime

from smart_fridge.lib.schemas.user import USER_ID

from . import fields as f
from .abc import BaseSchema
from .fridge import FRIDGE_ID
from .product import PRODUCT_ID


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


class FridgeProductSchema(FridgeProductCreateSchema):
    id: int = FRIDGE_PRODUCT_ID
    owner_id: int = USER_ID
    created_at: datetime = CREATED_AT
    deleted_at: datetime | None = DELETED_AT(default=None)
