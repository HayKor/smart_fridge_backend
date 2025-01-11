from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .abc import AbstractModel


if TYPE_CHECKING:
    from .fridge_product import FridgeProductModel
    from .product_type import ProductTypeModel


class ProductModel(AbstractModel):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column("id", Integer(), primary_key=True, autoincrement=True)
    product_type_id: Mapped[int] = mapped_column("product_type_id", ForeignKey("product_types.id"), nullable=False)
    owner_id: Mapped[int] = mapped_column("owner_id", ForeignKey("users.id"), nullable=False)
    amount: Mapped[float]
    manufactured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    opened_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    product_type: Mapped["ProductTypeModel"] = relationship("ProductTypeModel", back_populates="products")
    fridge_product: Mapped["FridgeProductModel"] = relationship("FridgeProductModel", back_populates="product")
