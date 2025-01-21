from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from smart_fridge.bot.schedule.jobs.expiry import expiration_notifications


def set_scheduled_jobs(scheduler: AsyncIOScheduler, bot: Bot):
    scheduler.add_job(
        expiration_notifications,
        "cron",
        minute=0,
        args=(bot,),
    )
