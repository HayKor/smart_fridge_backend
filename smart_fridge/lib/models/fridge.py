from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .abc import AbstractModel


if TYPE_CHECKING:
    from .fridge_product import FridgeProductModel
    from .user import UserModel


class FridgeModel(AbstractModel):
    """Model representing a fridge owned by a user.

    This class defines the structure of the 'fridges' table in the database,
    which stores information about fridges that users own, including ownership details
    and the name of the fridge.

    Attributes:
        id (Mapped[int]): Unique identifier for the fridge, 
            automatically generated as an integer and serves as the primary key.
        owner_id (Mapped[int]): Foreign key referencing the user's ID in the 'users' table, 
            indicating which user owns this fridge. This field is mandatory.
        name (Mapped[str]): Name of the fridge, allowing users to identify their fridge 
            easily. This field is mandatory and should be a string.
        fridge_products (Mapped[list["FridgeProductModel"]]): Relationship to the FridgeProductModel, 
            representing the products stored in this fridge. This field allows for a one-to-many 
            relationship, where a fridge can contain multiple products. The cascade option 
            ensures that related fridge products are deleted if the fridge is deleted, 
            and orphaned products are also removed.
        owner (Mapped["UserModel"]): Relationship to the UserModel, allowing access to the 
            details of the user who owns this fridge. This field provides a way to navigate 
            back to the user from the fridge model.
    """
    __tablename__ = "fridges"
    id: Mapped[int] = mapped_column("id", Integer(), primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column("owner_id", ForeignKey("users.id"), nullable=False)
    name: Mapped[str]
    fridge_products: Mapped[list["FridgeProductModel"]] = relationship(
        "FridgeProductModel", back_populates="fridge", cascade="all, delete-orphan"
    )
    owner: Mapped["UserModel"] = relationship("UserModel")
