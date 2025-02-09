from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .abc import AbstractModel


if TYPE_CHECKING:
    from .product_type import ProductTypeModel


class CartProductModel(AbstractModel):
    """Model representing a product in a user's shopping cart.

    This class defines the structure of the 'cart_products' table in the database,
    which stores information about products added to a user's shopping cart, including
    ownership details, product type, and timestamps for creation and deletion.

    Attributes:
        id (Mapped[int]): Unique identifier for the cart product, 
            automatically generated as an integer and serves as the primary key.
        owner_id (Mapped[int]): Foreign key referencing the user's ID in the 'users' table, 
            indicating which user owns this cart product. This field is mandatory.
        product_type_id (Mapped[int]): Foreign key referencing the product type's ID in the 
            'product_types' table, indicating the type of product being added to the cart. 
            This field is mandatory.
        created_at (Mapped[datetime]): Timestamp indicating when the cart product was created, 
            automatically set to the current time in UTC. This field is mandatory.
        deleted_at (Mapped[datetime | None]): Timestamp indicating when the cart product was 
            deleted from the cart, if applicable. This field is optional and can be null, 
            allowing for soft deletion.
    
    Relationships:
        product_type (Mapped["ProductTypeModel"]): Relationship to the ProductTypeModel, 
            allowing access to the details of the product type associated with this cart product.
    """
    __tablename__ = "cart_products"
    id: Mapped[int] = mapped_column("id", Integer(), primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column("owner_id", ForeignKey("users.id"), nullable=False)
    product_type_id: Mapped[int] = mapped_column("product_type_id", ForeignKey("product_types.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    product_type: Mapped["ProductTypeModel"] = relationship("ProductTypeModel", back_populates="cart_products")
