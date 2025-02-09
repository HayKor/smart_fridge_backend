from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .abc import AbstractModel


if TYPE_CHECKING:
    from .fridge_product import FridgeProductModel
    from .product_type import ProductTypeModel


class ProductModel(AbstractModel):
    """Model representing a product in the inventory.

    This class defines the structure of the 'products' table in the database,
    which stores information about products available for users, including
    ownership details, product type, and timestamps for manufacturing and opening.

    Attributes:
        id (Mapped[int]): Unique identifier for the product, 
            automatically generated as an integer and serves as the primary key.
        product_type_id (Mapped[int]): Foreign key referencing the product type's ID in the 
            'product_types' table, indicating the type of product. This field is mandatory.
        owner_id (Mapped[int]): Foreign key referencing the user's ID in the 'users' table, 
            indicating which user owns this product. This field is mandatory.
        amount (Mapped[float]): The quantity of the product available in stock. 
            This field is mandatory and should be a non-negative value.
        manufactured_at (Mapped[datetime]): Timestamp indicating when the product was 
            manufactured, automatically set to the current time in UTC. This field is mandatory.
        opened_at (Mapped[datetime | None]): Timestamp indicating when the product was 
            opened or made available for use, if applicable. This field is optional and can be null, 
            allowing for products that have not yet been opened.

    Relationships:
        product_type (Mapped["ProductTypeModel"]): Relationship to the ProductTypeModel, 
            allowing access to the details of the product type associated with this product.
        fridge_product (Mapped["FridgeProductModel"]): Relationship to the FridgeProductModel, 
            allowing access to the details of the fridge product associated with this product.
    """
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
