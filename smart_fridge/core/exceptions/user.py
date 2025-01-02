from .abc import AbstractException, ConflictException, NotFoundException, UnauthorizedException


class UserException(AbstractException):
    """Base user exception."""


class UserNotFoundException(UserException, NotFoundException):
    """User not found."""

    detail = "User not found"


class UserUnauthorizedException(UserException, UnauthorizedException):
    """User unauthorized"""

    detail = "User unauthorized"


class UserDeletedException(UserException, ConflictException):
    """User deleted."""

    detail = "User deleted"


class UserEmailAlreadyExistsException(UserException, ConflictException):
    """User email already exists."""

    auto_additional_info_fields = ["email"]

    detail = "User with email {email} already exists, please use another email"
