from fastapi import APIRouter

from smart_fridge.core.dependencies.fastapi import DatabaseDependency
from smart_fridge.lib.db import product_type as product_types_db
from smart_fridge.lib.schemas.product_type import (
    ProductTypeCreateSchema,
    ProductTypePatchSchema,
    ProductTypeSchema,
    ProductTypeUpdateSchema,
)


router = APIRouter(prefix="/product_types", tags=["product_types"])


@router.post("/", response_model=ProductTypeSchema)
async def create_product_type(db: DatabaseDependency, schema: ProductTypeCreateSchema) -> ProductTypeSchema:
    return await product_types_db.create_product_type(db, schema=schema)


# TODO: add filters & pagination
@router.get("/", response_model=list[ProductTypeSchema])
async def get_product_types(db: DatabaseDependency) -> list[ProductTypeSchema]:
    return await product_types_db.get_product_types(db)


@router.get("/{id}", response_model=ProductTypeSchema)
async def get_product_type(db: DatabaseDependency, id: int) -> ProductTypeSchema:
    return await product_types_db.get_product_type(db, product_type_id=id)


@router.patch("/{id}", response_model=ProductTypeSchema)
async def patch_product_type(db: DatabaseDependency, id: int, schema: ProductTypePatchSchema) -> ProductTypeSchema:
    return await product_types_db.update_product_type(db, product_type_id=id, schema=schema)


@router.put("/{id}", response_model=ProductTypeSchema)
async def update_product_type(db: DatabaseDependency, id: int, schema: ProductTypeUpdateSchema) -> ProductTypeSchema:
    return await product_types_db.update_product_type(db, product_type_id=id, schema=schema)


@router.delete("/{id}", status_code=204)
async def delete_product_type(db: DatabaseDependency, id: int) -> None:
    return await product_types_db.delete_product_type(db, product_type_id=id)
