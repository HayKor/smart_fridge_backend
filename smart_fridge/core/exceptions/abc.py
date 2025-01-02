from abc import ABCMeta
from logging import getLogger
from typing import Any, Generic, Sequence, TypedDict, TypeVar
from uuid import UUID, uuid4

from fastapi import status


logger = getLogger(__name__)

_Exception = TypeVar("_Exception", bound=Exception)


class ExceptionConfigDict(TypedDict, total=False):

    detail: str | None
    status_code: int
    headers: dict[str, str] | None
    log_exception: bool
    log_items: list[str]
    log_instantly: bool
    is_public: bool
    additional_info: dict[str, Any]
    auto_additional_info_fields: Sequence[str]
    format_detail_from_kwargs: bool


class ApiException(Exception):
    """Base exception for API."""


class AbstractException(ApiException, metaclass=ABCMeta):
    """Abstract exception.

    All custom http exceptions must inherit from this class.

    Example:
    ```
        class MyException(AbstractException):
            status_code = status.HTTP_400_BAD_REQUEST
            detail = "My custom exception"
            headers = {"X-Error": "There goes my error"}

        class MyExceptionWithInit(AbstractException):
            def __init__(
                self,
                detail: str = "My custom exception",
                status_code: int = status.HTTP_400_BAD_REQUEST,
                headers: dict[str, str] = {"X-Error": "There goes my error"},
            ) -> None:
                # In __init__ we can do more complex logic, like setting status_code
                # based on some condition.
                super().__init__(detail, status_code, headers)
    ```
    """

    detail: str | None = None
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    headers: dict[str, str] | None = None
    log_exception: bool = True
    log_items: list[str] = []
    log_instantly: bool = False
    is_public: bool = True
    additional_info: dict[str, Any] = {}
    auto_additional_info_fields: Sequence[str] = []
    format_detail_from_kwargs: bool = True

    def __init__(
        self,
        detail_: str | None = None,
        status_code_: int | None = None,
        *,
        headers_: dict[str, str] | None = None,
        log_exception_: bool | None = None,
        request_id_: UUID | None = None,
        is_public_: bool | None = None,
        additional_info_: dict[str, Any] | None = None,
        **kwargs: Any,
    ):
        """Exception init method.

        Args:
            detail_: Short error description.
            status_code_: HTTP status code that will be returned.
            headers_: Dict with HTTP headers that will be returned.
            log_exception_: If True, then log the exception to the console.
            request_id_: Ramdom request ID to link the exception to the request.
            is_public_: If True, then the exception is public.
            additional_info_: Additional public computer-readable information.
        """
        self.current_request_id = request_id_ or uuid4()
        self.current_detail = detail_ or self.detail
        self.current_headers = headers_ or self.headers
        self.current_status_code = status_code_ or self.status_code
        self.current_log_exception = log_exception_ or self.log_exception
        self.current_is_public = is_public_ or self.is_public
        self.current_additional_info = additional_info_ or self.additional_info.copy()
        # Format detail from kwargs
        if kwargs and self.current_detail is not None and self.format_detail_from_kwargs:
            try:
                self.current_detail = self.current_detail.format_map(kwargs)
            except KeyError:
                logger.exception(
                    "Failed to format detail from kwargs. (reqid: %s)",
                    self.current_request_id,
                )
        # Add additional info fields from kwargs
        if kwargs and self.auto_additional_info_fields:
            for field in self.auto_additional_info_fields:
                if field in kwargs:
                    field_value = kwargs[field]
                    if type(kwargs[field]) in (UUID,):
                        field_value = str(field_value)
                    self.current_additional_info[field] = field_value
        # If detail is specified, then pass it to Exception() constructor.
        # This logs the exception with detail to the console.
        if self.current_detail is not None:
            super().__init__(self.current_detail)
        else:
            # If detail is not specified, then pass the class name to Exception() constructor.
            # Example: "NotFoundException (404)."
            super().__init__(f"{self.__class__.__name__} ({self.current_status_code}).")
        # Add kwargs to the exception object.
        for key, value in kwargs.items():
            if key in [
                "detail",
                "status_code",
                "headers",
                "log_exception",
                "request_id",
                "is_public",
                "additional_info",
            ]:
                logger.warning(
                    "Exception attribute set %s is ignored. (reqid: %s)",
                    key,
                    self.current_request_id,
                )
                continue
            setattr(self, key, value)
        # Log exception to the console.
        if self.log_instantly:
            self._log()

    def __repr__(self) -> str:
        """Str repr."""
        return (
            f"<{self.__class__.__name__} (code: {self.current_status_code}, "
            f"reqid: {self.current_request_id or 'no id'})> " + (self.current_detail or "no detail")
        )

    def __str__(self) -> str:
        """Str repr."""
        return self.__repr__()

    def _log(self) -> None:
        """Log exception."""
        if not self.current_log_exception:
            return

        text = ""
        # Add log items
        if self.log_items:
            text += "Exception log items:"
            for item in self.log_items:
                item_obj = getattr(self, item)
                text += f"\n- {item}: {item_obj}"
        # Log exception to the console.
        logger.exception(text, exc_info=self)


class ExceptionExcInfo(AbstractException, Generic[_Exception]):
    """Abstract exception with exception information."""

    exception: _Exception | None = None
    log_items = ["exception"]

    def __init__(
        self,
        detail_: str | None = None,
        status_code_: int | None = None,
        exception: _Exception | None = None,
        *,
        headers_: dict[str, str] | None = None,
        log_exception_: bool | None = None,
        request_id_: UUID | None = None,
        is_public_: bool | None = None,
        additional_info_: dict[str, Any] | None = None,
        **kwargs: Any,
    ):
        super().__init__(
            detail_,
            status_code_,
            exception=exception,
            headers_=headers_,
            log_exception_=log_exception_,
            request_id_=request_id_,
            is_public_=is_public_,
            additional_info_=additional_info_,
            **kwargs,
        )


# Define base exceptions for specific HTTP status codes.
# Usage: class MyDomainException(DomainException, NotFoundException): pass
# Order is important here, please see the comment in AbstractException.__init__.
class BadRequestException(AbstractException):
    """400 Bad Request."""

    status_code = status.HTTP_400_BAD_REQUEST


class UnauthorizedException(AbstractException):
    """401 Unauthorized."""

    status_code = status.HTTP_401_UNAUTHORIZED


class ForbiddenException(AbstractException):
    """403 Forbidden."""

    status_code = status.HTTP_403_FORBIDDEN


class NotFoundException(AbstractException):
    """404 Not Found."""

    status_code = status.HTTP_404_NOT_FOUND


class MethodNotAllowedException(AbstractException):
    """405 Method Not Allowed."""

    status_code = status.HTTP_405_METHOD_NOT_ALLOWED


class ConflictException(AbstractException):
    """409 Conflict."""

    status_code = status.HTTP_409_CONFLICT


class UnprocessableEntityException(AbstractException):
    """422 Unprocessable Entity."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


class InternalServerErrorException(AbstractException):
    """500 Internal Server Error."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class NotImplementedException(AbstractException):
    """501 Not Implemented."""

    status_code = status.HTTP_501_NOT_IMPLEMENTED


class ServiceUnavailableException(AbstractException):
    """503 Service Unavailable."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
