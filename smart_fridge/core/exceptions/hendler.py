import logging
from uuid import UUID, uuid4

from fastapi import Request
from fastapi.responses import JSONResponse

from .abc import AbstractException
from .schema import ErrorSchema


logger = logging.getLogger(__name__)

EMPTY_EXCEPTION_UUID = "00000000-0000-0000-0000-000000000000"


async def abstract_exception_handler(request: Request, exc: AbstractException, log: bool = True) -> JSONResponse:
    return JSONResponse(
        status_code=exc.current_status_code,
        content=ErrorSchema(
            error_code=exc.__class__.__name__,
            detail=exc.current_detail,
            event_id=str(exc.current_request_id),
            additional_info=exc.current_additional_info,
        ).model_dump(mode="json"),
        headers=exc.current_headers,
    )


async def unknown_exception_handler(request: Request, exc: Exception, id_: UUID | None = None) -> JSONResponse:
    if id_ is None:
        id_ = uuid4()
    logger.exception(f"({id_}) Unknown exception occurred. Details:")

    return JSONResponse(
        status_code=500,
        content=ErrorSchema(
            error_code="UnknownException",
            detail="Unknown exception occurred.",
            event_id=str(id_),
            additional_info={},
        ).model_dump(mode="json"),
    )
