from aiogram import Bot
from apscheduler.executors.base import logging
from sqlalchemy.ext.asyncio import AsyncSession

from smart_fridge.core.dependencies.aiogram import container
from smart_fridge.lib.db import user as users_db


logger = logging.getLogger(__name__)


async def _send_notification(bot: Bot, tg_id: int, days: int) -> None:
    try:
        await bot.send_message(
            chat_id=tg_id,
            text=f"<b>Внимание</b>! У одного из ваших продуктов в холодильнике срок годности истекает через <code>{days}</code> дней.",
        )
    except:
        pass


async def expiration_notifications(bot: Bot) -> None:
    async with container() as request_container:
        db = await request_container.get(AsyncSession)

        results = await users_db.get_expiry_users(db)
        logger.debug("Got expiry users results: %s", results)
        for result in results:
            user, days = result
            if days <= 3:
                await _send_notification(bot, user.tg_id, days)
