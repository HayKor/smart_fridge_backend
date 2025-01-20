import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka

from smart_fridge.bot.handlers import router
from smart_fridge.core.config import AppConfig
from smart_fridge.core.dependencies.aiogram import provider


async def main():
    container = make_async_container(provider)

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s   %(name)-25s %(levelname)-8s %(message)s",
    )

    config = await container.get(AppConfig)

    bot = Bot(token=config.bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp.include_router(router)

    setup_dishka(container=container, router=dp, auto_inject=True)

    try:
        # THIS GOES LAST
        await dp.start_polling(bot)

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
