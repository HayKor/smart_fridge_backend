from datetime import datetime

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

from .abc import AbstractModel


class UserModel(AbstractModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column("id", Integer(), primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(index=True)
    email: Mapped[str] = mapped_column(index=True)
    hashed_password: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
