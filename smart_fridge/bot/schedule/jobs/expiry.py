from typing import TYPE_CHECKING

from apscheduler.executors.base import logging
from sqlalchemy.ext.asyncio import AsyncSession

from smart_fridge.lib.db import user as users_db


if TYPE_CHECKING:
    from smart_fridge.bot.app import BotApp


logger = logging.getLogger(__name__)


async def _send_notification(bot_app: "BotApp", tg_id: int, days: int) -> None:
    try:
        await bot_app.bot.send_message(
            chat_id=tg_id,
            text=f"<b>Внимание</b>! У одного из ваших продуктов в холодильнике срок годности истекает через <code>{days}</code> дней.",
        )
    except:
        pass


async def expiration_notifications(bot_app: "BotApp") -> None:
    async with bot_app.container() as request_container:
        db = await request_container.get(AsyncSession)

        results = await users_db.get_expiry_users(db)
        logger.debug("Got expiry users results: %s", results)
        for result in results:
            user, days = result
            if days <= 3:
                await _send_notification(bot_app, user.tg_id, days)
