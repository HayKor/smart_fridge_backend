from typing import Sequence

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from smart_fridge.lib.schemas.job import BaseJob


def set_scheduled_jobs(scheduler: AsyncIOScheduler, jobs: Sequence[BaseJob]) -> None:
    for job in jobs:
        scheduler.add_job(**job.model_dump())
