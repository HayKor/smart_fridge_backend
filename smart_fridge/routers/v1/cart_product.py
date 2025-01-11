from fastapi import APIRouter, Depends

from smart_fridge.core.dependencies.fastapi import DatabaseDependency, TokenDataDependency
from smart_fridge.lib.db import cart_product as cart_products_db
from smart_fridge.lib.schemas.cart_product import (
    CartProductCreateSchema,
    CartProductPaginationResponse,
    CartProductPatchSchema,
    CartProductSchema,
    CartProductUpdateSchema,
)
from smart_fridge.lib.schemas.pagination import PaginationRequest


router = APIRouter(prefix="/cart_products", tags=["cart_products"])


@router.post("/", response_model=CartProductSchema)
async def create_cart_product(
    db: DatabaseDependency, schema: CartProductCreateSchema, token_data: TokenDataDependency
) -> CartProductSchema:
    return await cart_products_db.create_cart_product(db, token_data.user_id, schema)
