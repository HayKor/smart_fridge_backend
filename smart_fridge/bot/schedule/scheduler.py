from typing import TYPE_CHECKING

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from smart_fridge.bot.schedule.jobs.expiry import expiration_notifications


if TYPE_CHECKING:
    from smart_fridge.bot.app import BotApp


def set_scheduled_jobs(scheduler: AsyncIOScheduler, bot_app: "BotApp") -> None:
    scheduler.add_job(
        expiration_notifications,
        "cron",
        minute=0,
        args=(bot_app,),
    )
