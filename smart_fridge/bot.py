import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from dishka import FromDishka
from dishka.integrations.aiogram import setup_dishka
from sqlalchemy.ext.asyncio import AsyncSession

from smart_fridge.core.config import AppConfig
from smart_fridge.core.dependencies.aiogram import container


async def main():
    logging.basicConfig(level=logging.DEBUG)

    config = await container.get(AppConfig)

    bot = Bot(
        token=config.bot.token,
    )
    dp = Dispatcher()

    @dp.message()
    async def f(message: types.Message, db: FromDishka[AsyncSession]):
        await message.answer(text=str(message.from_user.id))

    setup_dishka(
        container=container,
        router=dp,
        auto_inject=True,
    )

    try:
        # THIS GOES LAST
        await dp.start_polling(bot)

    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
