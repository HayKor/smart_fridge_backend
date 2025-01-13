from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .abc import AbstractModel


if TYPE_CHECKING:
    from .product_type import ProductTypeModel


class CartProductModel(AbstractModel):
    __tablename__ = "cart_products"
    id: Mapped[int] = mapped_column("id", Integer(), primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column("owner_id", ForeignKey("users.id"), nullable=False)
    product_type_id: Mapped[int] = mapped_column("product_type_id", ForeignKey("product_types.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    product_type: Mapped["ProductTypeModel"] = relationship("ProductTypeModel", back_populates="cart_products")
