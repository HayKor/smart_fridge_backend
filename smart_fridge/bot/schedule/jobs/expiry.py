from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from smart_fridge.core.dependencies.aiogram import container
from smart_fridge.lib.db import user as users_db


async def _send_notification(bot: Bot, tg_id: int, days: int) -> None:
    try:
        await bot.send_message(
            chat_id=tg_id,
            text=f"Внимание! У одного из ваших продуктов в холодильнике срок годности истекает через {days}",
        )
    except:
        pass


async def expiration_notifications(bot: Bot) -> None:
    async with container() as request_container:
        db = await request_container.get(AsyncSession)

        generator = users_db.get_expiry_users(db)
        async for res in generator:
            tg_id, days = res
            await _send_notification(bot, tg_id, days)
