from fastapi import APIRouter

from . import auth, user


router = APIRouter(prefix="/v1")

for i in [
    auth.router,
    user.router,
]:
    router.include_router(i)
