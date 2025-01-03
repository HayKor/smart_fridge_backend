from fastapi import APIRouter

from . import auth, product, product_type, user


router = APIRouter(prefix="/v1")

for i in [
    auth.router,
    user.router,
    product_type.router,
    product.router,
]:
    router.include_router(i)
