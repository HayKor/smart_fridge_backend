from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .abc import AbstractModel


if TYPE_CHECKING:
    from .fridge_product import FridgeProductModel
    from .user import UserModel


class FridgeModel(AbstractModel):
    __tablename__ = "fridges"
    id: Mapped[int] = mapped_column("id", Integer(), primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column("owner_id", ForeignKey("users.id"), nullable=False)
    name: Mapped[str]
    fridge_products: Mapped[list["FridgeProductModel"]] = relationship("FridgeProductModel", back_populates="fridge")
    owner: Mapped["UserModel"] = relationship("UserModel")
