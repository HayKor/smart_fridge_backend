from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .abc import AbstractModel


if TYPE_CHECKING:
    from .fridge import FridgeModel
    from .product import ProductModel


class FridgeProductModel(AbstractModel):
    __tablename__ = "fridge_products"
    id: Mapped[int] = mapped_column("id", Integer(), primary_key=True, autoincrement=True)
    fridge_id: Mapped[int] = mapped_column("fridge_id", ForeignKey("fridges.id"), nullable=False)
    product_id: Mapped[int] = mapped_column("product_id", ForeignKey("products.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fridge: Mapped["FridgeModel"] = relationship("FridgeModel", back_populates="fridge_products")
    product: Mapped["ProductModel"] = relationship("ProductModel")
