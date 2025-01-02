from enum import StrEnum

from sqlalchemy import Enum, Integer, Interval
from sqlalchemy.orm import Mapped, mapped_column

from .abc import AbstractModel


class AccountType(StrEnum):
    VOLUME = "volume"
    WEIGHT = "weight"
    PIECES = "pieces"


class ProductTypesModel(AbstractModel):
    __tablename__ = "product_types"
    id: Mapped[int] = mapped_column("id", Integer(), primary_key=True, autoincrement=True)
    name: Mapped[str]
    slug: Mapped[str]
    account_type: Mapped[AccountType] = mapped_column(Enum(AccountType))
    exp_period_before_opening: Mapped[Interval]
    exp_period_after_opening: Mapped[Interval | None]
    calories: Mapped[int | None]
