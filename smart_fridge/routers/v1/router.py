from fastapi import APIRouter

from . import auth, fridge, fridge_product, product, product_type, user


router = APIRouter(prefix="/v1")

for i in [
    auth.router,
    user.router,
    product_type.router,
    product.router,
    fridge_product.router,
    fridge.router,
]:
    router.include_router(i)
