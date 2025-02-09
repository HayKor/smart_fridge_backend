from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .abc import AbstractModel


if TYPE_CHECKING:
    from .fridge import FridgeModel
    from .product import ProductModel


class FridgeProductModel(AbstractModel):
    """Model representing a product stored in a user's fridge.

    This class defines the structure of the 'fridge_products' table in the database,
    which stores information about products that are currently stored in a user's fridge,
    including references to the fridge and the product itself, as well as timestamps for 
    creation and deletion.

    Attributes:
        id (Mapped[int]): Unique identifier for the fridge product, 
            automatically generated as an integer and serves as the primary key.
        fridge_id (Mapped[int]): Foreign key referencing the fridge's ID in the 
            'fridges' table, indicating which fridge contains this product. 
            This field is mandatory.
        product_id (Mapped[int]): Foreign key referencing the product's ID in the 
            'products' table, indicating which product is stored in the fridge. 
            This field is mandatory.
        created_at (Mapped[datetime]): Timestamp indicating when the fridge product was created, 
            automatically set to the current time in UTC. This field is mandatory.
        deleted_at (Mapped[datetime | None]): Timestamp indicating when the fridge product was 
            deleted from the fridge, if applicable. This field is optional and can be null, 
            allowing for soft deletion.
    
    Relationships:
        fridge (Mapped["FridgeModel"]): Relationship to the FridgeModel, 
            allowing access to the details of the fridge that contains this product.
        product (Mapped["ProductModel"]): Relationship to the ProductModel, 
            allowing access to the details of the product stored in the fridge.
    """
    __tablename__ = "fridge_products"
    id: Mapped[int] = mapped_column("id", Integer(), primary_key=True, autoincrement=True)
    fridge_id: Mapped[int] = mapped_column("fridge_id", ForeignKey("fridges.id"), nullable=False)
    product_id: Mapped[int] = mapped_column("product_id", ForeignKey("products.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    fridge: Mapped["FridgeModel"] = relationship("FridgeModel", back_populates="fridge_products")
    product: Mapped["ProductModel"] = relationship("ProductModel", back_populates="fridge_product")
