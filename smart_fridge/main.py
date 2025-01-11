from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from smart_fridge.core.config import AppConfig
from smart_fridge.core.dependencies import constructors as app_depends, fastapi as stubs
from smart_fridge.core.exceptions.abc import AbstractException
from smart_fridge.core.exceptions.schema import ErrorSchema
from smart_fridge.routers import router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    config = AppConfig.from_env()
    async with asynccontextmanager(app_depends.redis_pool)(config.redis.url) as redis_pool:
        with contextmanager(app_depends.db_session_maker)(config.database.url) as maker:
            app.dependency_overrides[stubs.app_config_stub] = lambda: config
            app.dependency_overrides[stubs.db_session_maker_stub] = lambda: maker
            app.dependency_overrides[stubs.redis_conn_pool_stub] = lambda: redis_pool

            yield


app = FastAPI(
    lifespan=lifespan,
)


@app.exception_handler(AbstractException)
async def http_exception_handler(request: Request, exc: AbstractException) -> JSONResponse:
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


app.include_router(router)
