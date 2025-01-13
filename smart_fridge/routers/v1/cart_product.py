from fastapi import APIRouter, Depends

from smart_fridge.core.dependencies.fastapi import DatabaseDependency, TokenDataDependency
from smart_fridge.lib.db import cart_product as cart_products_db
from smart_fridge.lib.schemas.cart_product import (
    CartProductCreateSchema,
    CartProductPatchSchema,
    CartProductSchema,
    CartProductUpdateSchema,
)


router = APIRouter(prefix="/cart_products", tags=["cart_products"])


@router.post("/", response_model=CartProductSchema)
async def create_cart_product(
    db: DatabaseDependency, schema: CartProductCreateSchema, token_data: TokenDataDependency
) -> CartProductSchema:
    return await cart_products_db.create_cart_product(db, token_data.user_id, schema)


@router.get("/", response_model=list[CartProductSchema])
async def get_cart_products(db: DatabaseDependency, token_data: TokenDataDependency) -> list[CartProductSchema]:
    return await cart_products_db.get_cart_products(db, token_data.user_id)


@router.get("/{cart_product_id}", response_model=CartProductSchema)
async def get_cart_product(
    db: DatabaseDependency, cart_product_id: int, token_data: TokenDataDependency
) -> CartProductSchema:
    return await cart_products_db.get_cart_product(db, cart_product_id, token_data.user_id)


@router.patch("/{cart_product_id}", response_model=CartProductSchema)
async def patch_cart_product(
    db: DatabaseDependency, cart_product_id: int, token_data: TokenDataDependency, schema: CartProductPatchSchema
) -> CartProductSchema:
    return await cart_products_db.update_cart_product(db, cart_product_id, schema, token_data.user_id)


@router.put("/{cart_product_id}", response_model=CartProductSchema)
async def update_cart_product(
    db: DatabaseDependency, cart_product_id: int, token_data: TokenDataDependency, schema: CartProductUpdateSchema
) -> CartProductSchema:
    return await cart_products_db.update_cart_product(db, cart_product_id, schema, token_data.user_id)


@router.delete("/{cart_product_id}", status_code=204)
async def delete_cart_product(db: DatabaseDependency, cart_product_id: int, token_data: TokenDataDependency) -> None:
    return await cart_products_db.delete_cart_product(db, cart_product_id, token_data.user_id)
