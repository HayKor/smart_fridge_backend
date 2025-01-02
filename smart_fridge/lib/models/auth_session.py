from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID as PyUUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Uuid as SqlUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .abc import AbstractModel


if TYPE_CHECKING:
    from .user import UserModel


class AuthSessionModel(AbstractModel):
    __tablename__ = "auth_sessions"
    id: Mapped[PyUUID] = mapped_column("id", SqlUUID(native_uuid=True, as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column("user_id", ForeignKey("users.id"), nullable=False)
    user_ip: Mapped[str] = mapped_column("user_ip", String(128), nullable=False)
    user_agent: Mapped[str | None] = mapped_column("user_agent", String(256), nullable=True)
    access_token: Mapped[PyUUID | None] = mapped_column(
        "access_token", SqlUUID(native_uuid=True, as_uuid=True), nullable=True, default=uuid4
    )
    refresh_token: Mapped[PyUUID | None] = mapped_column(
        "refresh_token", SqlUUID(native_uuid=True, as_uuid=True), nullable=True, default=uuid4
    )
    created_at: Mapped[datetime] = mapped_column(
        "created_at", DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    # relationships
    user: Mapped["UserModel"] = relationship("UserModel")
