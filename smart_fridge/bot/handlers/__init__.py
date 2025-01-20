from aiogram import Router

from . import common


router = Router(name=__name__)

for i in [
    common.router,
]:
    router.include_router(i)
