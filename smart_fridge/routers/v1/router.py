from fastapi import APIRouter

from . import auth, cart_product, fridge, fridge_product, product, product_type, statistics, user


router = APIRouter(prefix="/v1")

for i in [
    auth.router,
    user.router,
    product_type.router,
    product.router,
    fridge_product.router,
    fridge.router,
    cart_product.router,
    statistics.router,
]:
    router.include_router(i)
