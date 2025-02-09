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
    """Model representing a type of product available in the system.

    This class defines the structure of the 'product_types' table in the database,
    which stores information about different types of products, including their 
    names, slugs, account types, expiration periods, and nutritional information.

    Attributes:
        id (Mapped[int]): Unique identifier for the product type, 
            automatically generated as an integer and serves as the primary key.
        name (Mapped[str]): The name of the product type, which is a human-readable 
            string used to identify the type of product.
        slug (Mapped[str]): A URL-friendly version of the product type name, 
            typically used in web addresses to refer to this product type.
        account_type (Mapped[AccountType]): An enumeration indicating the type of 
            account that can access this product type, ensuring that only 
            authorized users can utilize certain product types.
        exp_period_before_opening (Mapped[timedelta]): The duration before the 
            product type can be opened or accessed, represented as a timedelta.
        exp_period_after_opening (Mapped[timedelta | None]): The duration after 
            the product type has been opened during which it remains valid. This 
            field is optional and can be null, indicating no expiration after opening.
        calories (Mapped[int | None]): The caloric content of the product type, 
            represented as an integer. This field is optional and can be null if 
            the caloric information is not applicable or unknown.

    Relationships:
        products (Mapped[list["ProductModel"]]): Relationship to the ProductModel, 
            allowing access to the list of products associated with this product type.
        cart_products (Mapped[list["CartProductModel"]]): Relationship to the 
            CartProductModel, allowing access to the list of cart products 
            associated with this product type.
    """
    __tablename__ = "product_types"
    id: Mapped[int] = mapped_column("id", Integer(), primary_key=True, autoincrement=True)
    name: Mapped[str]
    slug: Mapped[str]
    account_type: Mapped[AccountType] = mapped_column(Enum(AccountType))
    exp_period_before_opening: Mapped[timedelta]
    exp_period_after_opening: Mapped[timedelta | None]
    calories: Mapped[int | None]
    products: Mapped[list["ProductModel"]] = relationship("ProductModel", back_populates="product_type")
    cart_products: Mapped[list["CartProductModel"]] = relationship("CartProductModel", back_populates="product_type")
