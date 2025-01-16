from typing import Any, AsyncGenerator, Generator

from aiogram.types import TelegramObject
from dishka import Provider, Scope, make_async_container, provide
from dishka.integrations.aiogram import AiogramProvider
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from smart_fridge.core.config import AppConfig

from . import constructors as app_depends


class AppProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_app_config(self) -> AppConfig:
        return AppConfig.from_env()


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_maker(self, config: AppConfig) -> sessionmaker[Any]:
        return next(app_depends.db_session_maker(config.database.url))

    # See: https://dishka.readthedocs.io/en/stable/integrations/aiogram.html
    @provide(scope=Scope.REQUEST)
    async def provide_db_session(
        self, maker: sessionmaker[Any], event: TelegramObject
    ) -> AsyncGenerator[AsyncSession, None]:
        generator = app_depends.db_session_autocommit(maker)
        session = await anext(generator)

        yield session

        try:
            await anext(generator)
        except StopAsyncIteration:
            pass
        else:
            raise RuntimeError("Database session not closed (db dependency generator is not closed).")


container = make_async_container(AppProvider(), DatabaseProvider(), AiogramProvider())
