from .abc import AbstractException, NotFoundException


class AuthSessionException(AbstractException):
    """Base auth session exception."""


class AuthSessionNotFoundException(AuthSessionException, NotFoundException):
    """Auth session not found."""

    detail = "Auth session not found"
