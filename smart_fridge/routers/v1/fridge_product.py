from fastapi import APIRouter

from smart_fridge.core.dependencies.fastapi import DatabaseDependency, TokenDataDependency
from smart_fridge.lib.db import fridge_product as fridge_products_db
from smart_fridge.lib.schemas.fridge_product import (
    FridgeProductCreateSchema,
    FridgeProductPatchSchema,
    FridgeProductSchema,
    FridgeProductUpdateSchema,
)


router = APIRouter(prefix="/fridge_products", tags=["fridge_products"])


@router.post("/", response_model=FridgeProductSchema)
async def create_fridge_product(db: DatabaseDependency, schema: FridgeProductCreateSchema) -> FridgeProductSchema:
    return await fridge_products_db.create_fridge_product(db, schema)


@router.get("/{id}", response_model=FridgeProductSchema)
async def get_fridge_product(db: DatabaseDependency, id: int, token_data: TokenDataDependency) -> FridgeProductSchema:
    return await fridge_products_db.get_fridge_product(db, id, token_data.user_id)


@router.patch("/{id}", response_model=FridgeProductSchema)
async def patch_fridge_product(
    db: DatabaseDependency, id: int, token_data: TokenDataDependency, schema: FridgeProductPatchSchema
) -> FridgeProductSchema:
    return await fridge_products_db.update_fridge_product(db, id, schema, token_data.user_id)


@router.put("/{id}", response_model=FridgeProductSchema)
async def update_fridge_product(
    db: DatabaseDependency, id: int, token_data: TokenDataDependency, schema: FridgeProductUpdateSchema
) -> FridgeProductSchema:
    return await fridge_products_db.update_fridge_product(db, id, schema, token_data.user_id)


@router.delete("/{id}", status_code=204)
async def delete_fridge_product(db: DatabaseDependency, id: int, token_data: TokenDataDependency) -> None:
    return await fridge_products_db.delete_fridge_product(db, id, token_data.user_id)
