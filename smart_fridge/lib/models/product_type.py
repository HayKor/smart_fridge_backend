from datetime import timedelta
from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .abc import AbstractModel


if TYPE_CHECKING:
    from .cart_product import CartProductModel
    from .product import ProductModel


class AccountType(StrEnum):
    VOLUME = "volume"
    WEIGHT = "weight"
    PIECES = "pieces"


class ProductTypeModel(AbstractModel):
    __tablename__ = "product_types"
    id: Mapped[int] = mapped_column("id", Integer(), primary_key=True, autoincrement=True)
    name: Mapped[str]
    slug: Mapped[str]
    account_type: Mapped[AccountType] = mapped_column(Enum(AccountType))
    exp_period_before_opening: Mapped[timedelta]
    exp_period_after_opening: Mapped[timedelta | None]
    calories: Mapped[int | None]
    products: Mapped[list["ProductModel"]] = relationship("ProductModel", back_populates="product_type")
    cart_products: Mapped[list["CartProductModel"]] = relationship("CartProductModel", back_populates="product_types")
