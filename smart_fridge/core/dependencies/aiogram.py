from typing import Any, AsyncGenerator

from aiogram.types import TelegramObject
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import Provider, Scope, make_async_container
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from smart_fridge.core.config import AppConfig

from . import constructors as app_depends


async def provide_db_session(maker: sessionmaker[Any]) -> AsyncGenerator[AsyncSession, None]:
    generator = app_depends.db_session_autocommit(maker)
    session = await anext(generator)

    yield session

    try:
        await anext(generator)
    except StopAsyncIteration:
        pass
    else:
        raise RuntimeError("Database session not closed (db dependency generator is not closed).")


def db_session_maker(config: AppConfig) -> sessionmaker[Any]:
    return next(app_depends.db_session_maker(config.database.url))


provider = Provider()
provider.from_context(provides=TelegramObject, scope=Scope.REQUEST)
provider.provide(AppConfig.from_env, scope=Scope.APP, provides=AppConfig)
provider.provide(db_session_maker, scope=Scope.APP, provides=sessionmaker[Any])
provider.provide(provide_db_session, scope=Scope.REQUEST, provides=AsyncSession)
provider.provide(lambda: AsyncIOScheduler(), scope=Scope.APP, provides=AsyncIOScheduler)

container = make_async_container(provider)
