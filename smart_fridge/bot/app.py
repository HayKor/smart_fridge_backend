from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka

from smart_fridge.bot.handlers import router
from smart_fridge.bot.middlewares.error import ErrorHandlingMiddleware
from smart_fridge.bot.schedule.scheduler import set_scheduled_jobs
from smart_fridge.core.config import AppConfig
from smart_fridge.core.dependencies.aiogram import provider


class BotApp:
    def __init__(self) -> None:
        self.container = make_async_container(provider)

    async def setup_app(self) -> None:
        self.config = await self.container.get(AppConfig)
        self.scheduler = await self.container.get(AsyncIOScheduler)
        # Create bot & dp instances
        self.bot = Bot(token=self.config.bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.dp = Dispatcher()
        # Include middlewares and routers
        self.dp.message.middleware(ErrorHandlingMiddleware())
        self.dp.include_router(router)
        # Setup
        set_scheduled_jobs(self.scheduler, self)
        setup_dishka(container=self.container, router=self.dp, auto_inject=True)

    async def run(self) -> None:
        await self.setup_app()

        try:
            self.scheduler.start()
            # THIS GOES LAST
            await self.dp.start_polling(self.bot)

        finally:
            await self.bot.session.close()
            await self.container.close()
