from . import fields as f
from .abc import BaseSchema
from .user import USER_ID


FRIDGE_ID = f.ID(description="Fridge ID.")
FRIDGE_NAME = f.BaseField(description="Fridge name", examples=["My Fridge #1"])


class BaseFridgeSchema(BaseSchema):
    name: str = FRIDGE_NAME


class FridgeCreateSchema(BaseFridgeSchema):
    pass


class FridgeUpdateSchema(FridgeCreateSchema):
    pass


class FridgePatchSchema(FridgeCreateSchema):
    pass


class FridgeSchema(FridgeCreateSchema):
    id: int = FRIDGE_ID
    owner_id: int = USER_ID
