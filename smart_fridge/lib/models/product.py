from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .abc import AbstractModel


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
