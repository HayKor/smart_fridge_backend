import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dishka.integrations.aiogram import setup_dishka

from smart_fridge.bot.handlers import router
from smart_fridge.bot.middlewares.error import ErrorHandlingMiddleware
from smart_fridge.bot.schedule.scheduler import set_scheduled_jobs
from smart_fridge.core.config import AppConfig
from smart_fridge.core.dependencies.aiogram import container


async def main():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s   %(name)-25s %(levelname)-8s %(message)s",
    )

    config = await container.get(AppConfig)
    scheduler = await container.get(AsyncIOScheduler)

    bot = Bot(token=config.bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()

    dp.message.middleware(ErrorHandlingMiddleware())
    dp.include_router(router)

    set_scheduled_jobs(scheduler, bot)

    setup_dishka(container=container, router=dp, auto_inject=True)

    try:
        scheduler.start()
        # THIS GOES LAST
        await dp.start_polling(bot)

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
