from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Self

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import AppConfig
from .core.dependencies import constructors as app_depends, fastapi as stubs
from .core.exceptions.handler import register_exception_handlers
from .routers import router


class App:
    def __init__(self, config: AppConfig, app: FastAPI | None = None) -> None:
        self.config = config
        self.app = app or FastAPI(
            title="SmartFridge",
            description="SmartFridge API.",
            lifespan=self.lifespan,
        )

        self.setup_app()

    @classmethod
    def from_env(cls) -> Self:
        return cls(AppConfig.from_env())

    def setup_app(self) -> None:
        self.app.include_router(router)
        # middlewares
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        # exception handler
        register_exception_handlers(self.app)

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncGenerator[None, None]:
        async with asynccontextmanager(app_depends.redis_pool)(self.config.redis.url) as redis_pool:
            with contextmanager(app_depends.db_session_maker)(self.config.database.url) as maker:
                app.dependency_overrides[stubs.app_config_stub] = lambda: self.config
                app.dependency_overrides[stubs.db_session_maker_stub] = lambda: maker
                app.dependency_overrides[stubs.redis_conn_pool_stub] = lambda: redis_pool

                yield


def app() -> FastAPI:
    return App.from_env().app