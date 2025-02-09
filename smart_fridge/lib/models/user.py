from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .abc import AbstractModel


if TYPE_CHECKING:
    from .product import ProductModel


class UserModel(AbstractModel):
    """Model representing a user in the system.

    This class defines the structure of the 'users' table in the database,
    which stores information about registered users, including their credentials,
    account status, and timestamps for account creation and deletion.

    Attributes:
        id (Mapped[int]): Unique identifier for the user, 
            automatically generated as an integer and serves as the primary key.
        username (Mapped[str]): The username chosen by the user, 
            which is indexed for quick lookup. This field is mandatory.
        email (Mapped[str]): The email address of the user, 
            which is also indexed for quick lookup. This field is mandatory.
        hashed_password (Mapped[str]): The hashed password of the user, 
            used for authentication. This field is mandatory.
        is_active (Mapped[bool]): A boolean flag indicating whether the user's account 
            is active. Defaults to True, meaning the account is active unless specified otherwise.
        tg_id (Mapped[int | None]): The Telegram ID of the user, 
            which is optional and can be null if the user has not linked their Telegram account.
        created_at (Mapped[datetime]): Timestamp indicating when the user account was created, 
            automatically set to the current time in UTC. This field is mandatory and indexed for performance.
        deleted_at (Mapped[datetime | None]): Timestamp indicating when the user account was 
            deleted, if applicable. This field is optional and can be null, allowing for soft deletion.
    
    Relationships:
        products (Mapped[list["ProductModel"]]): Relationship to the ProductModel, 
            allowing access to the products associated with this user.
    """
    __tablename__ = "users"
    id: Mapped[int] = mapped_column("id", Integer(), primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(index=True)
    email: Mapped[str] = mapped_column(index=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    tg_id: Mapped[int | None] = mapped_column(default=None)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    products: Mapped[list["ProductModel"]] = relationship("ProductModel")
