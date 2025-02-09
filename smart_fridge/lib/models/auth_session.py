from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID as PyUUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Uuid as SqlUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .abc import AbstractModel


if TYPE_CHECKING:
    from .user import UserModel


class AuthSessionModel(AbstractModel):
    """Model representing an authentication session for a user.

    This class defines the structure of the 'auth_sessions' table in the database,
    which stores information about user authentication sessions, including session 
    identifiers, user details, and timestamps for session creation.

    Attributes:
        id (Mapped[PyUUID]): Unique identifier for the authentication session, 
            automatically generated as a UUID and serves as the primary key.
        user_id (Mapped[int]): Foreign key referencing the user's ID in the 'users' table, 
            indicating which user this authentication session belongs to. This field is mandatory.
        user_ip (Mapped[str]): IP address of the user during the authentication session, 
            stored as a string. This field is mandatory.
        user_agent (Mapped[str | None]): User agent string from the user's device, 
            providing information about the browser and operating system. This field is optional 
            and can be null if not provided.
        access_token (Mapped[PyUUID | None]): Access token for the session, 
            used for authenticating API requests. This field is optional and can be null, 
            allowing for sessions without an access token.
        refresh_token (Mapped[PyUUID | None]): Refresh token for the session, 
            used to obtain new access tokens without requiring the user to log in again. 
            This field is optional and can be null, allowing for sessions without a refresh token.
        created_at (Mapped[datetime]): Timestamp indicating when the authentication session was created, 
            automatically set to the current time in UTC. This field is mandatory.

    Relationships:
        user (Mapped["UserModel"]): Relationship to the UserModel, 
            allowing access to the details of the user associated with this authentication session.
    """
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
    user: Mapped["UserModel"] = relationship("UserModel")
