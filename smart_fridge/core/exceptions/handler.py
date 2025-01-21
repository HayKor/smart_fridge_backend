import logging
from uuid import UUID, uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
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


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    id_ = uuid4()

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorSchema(
            error_code="Exception",
            detail=exc.detail,
            event_id=str(id_),
            additional_info={},
        ).model_dump(mode="json"),
    )


async def request_validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = exc.errors()
    for error in errors:
        if "ctx" in error:
            del error["ctx"]
        if "url" in error:
            del error["url"]
    schema = ErrorSchema(
        error_code="ValidationException",
        detail="Invalid request data.",
        event_id=EMPTY_EXCEPTION_UUID,
        additional_info={"errors": errors},
    ).model_dump(mode="json")
    return JSONResponse(
        status_code=422,
        content=schema,
    )


async def not_found_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    r = ErrorSchema(
        error_code="EndpointNotFoundException",
        detail="404 endpoint not found.",
        event_id=EMPTY_EXCEPTION_UUID,
        additional_info={},
    ).model_dump(mode="json")
    r["additional_info"]["urls"] = {
        "openapi": "/openapi.json",
        "docs": "/docs",
    }
    return JSONResponse(status_code=404, content=r)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AbstractException, abstract_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, request_validation_exception_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unknown_exception_handler)
    app.add_exception_handler(404, not_found_exception_handler)  # type: ignore[arg-type]
