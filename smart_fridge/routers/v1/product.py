from fastapi import APIRouter

from smart_fridge.core.dependencies.fastapi import DatabaseDependency, TokenDataDependency
from smart_fridge.lib.db import product as products_db
from smart_fridge.lib.schemas.product import ProductCreateSchema, ProductPatchSchema, ProductSchema, ProductUpdateSchema


router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductSchema)
async def create_product(
    db: DatabaseDependency, schema: ProductCreateSchema, token_data: TokenDataDependency
) -> ProductSchema:
    return await products_db.create_product(db, token_data.user_id, schema)


# TODO: add filters & pagination
@router.get("/", response_model=list[ProductSchema])
async def get_products(db: DatabaseDependency, token_data: TokenDataDependency) -> list[ProductSchema]:
    return await products_db.get_products(db, token_data.user_id)


@router.get("/{id}", response_model=ProductSchema)
async def get_product(db: DatabaseDependency, id: int) -> ProductSchema:
    return await products_db.get_product(db, id)


@router.patch("/{id}", response_model=ProductSchema)
async def patch_product(db: DatabaseDependency, id: int, schema: ProductPatchSchema) -> ProductSchema:
    return await products_db.update_product(db, id, schema)


@router.put("/{id}", response_model=ProductSchema)
async def update_product(db: DatabaseDependency, id: int, schema: ProductUpdateSchema) -> ProductSchema:
    return await products_db.update_product(db, id, schema)


@router.delete("/{id}", status_code=204)
async def delete_product(db: DatabaseDependency, id: int) -> None:
    return await products_db.delete_product(db, id)
