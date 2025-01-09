from fastapi import APIRouter

from smart_fridge.core.dependencies.fastapi import DatabaseDependency, TokenDataDependency
from smart_fridge.lib.db import fridge as fridges_db
from smart_fridge.lib.schemas.fridge import FridgeCreateSchema, FridgePatchSchema, FridgeSchema, FridgeUpdateSchema


router = APIRouter(prefix="/fridges", tags=["fridges"])


@router.post("/", response_model=FridgeSchema)
async def create_fridge(
    db: DatabaseDependency, schema: FridgeCreateSchema, token_data: TokenDataDependency
) -> FridgeSchema:
    return await fridges_db.create_fridge(db, token_data.user_id, schema)


# TODO: add filters & pagination
@router.get("/", response_model=list[FridgeSchema])
async def get_fridges(db: DatabaseDependency, token_data: TokenDataDependency) -> list[FridgeSchema]:
    return await fridges_db.get_fridges(db, token_data.user_id)


@router.get("/{id}", response_model=FridgeSchema)
async def get_fridge(db: DatabaseDependency, id: int, token_data: TokenDataDependency) -> FridgeSchema:
    return await fridges_db.get_fridge(db, id, token_data.user_id)


@router.patch("/{id}", response_model=FridgeSchema)
async def patch_fridge(
    db: DatabaseDependency, id: int, token_data: TokenDataDependency, schema: FridgePatchSchema
) -> FridgeSchema:
    return await fridges_db.update_fridge(db, id, schema, token_data.user_id)


@router.put("/{id}", response_model=FridgeSchema)
async def update_fridge(
    db: DatabaseDependency, id: int, token_data: TokenDataDependency, schema: FridgeUpdateSchema
) -> FridgeSchema:
    return await fridges_db.update_fridge(db, id, schema, token_data.user_id)


@router.delete("/{id}", status_code=204)
async def delete_fridge(db: DatabaseDependency, id: int, token_data: TokenDataDependency) -> None:
    return await fridges_db.delete_fridge(db, id, token_data.user_id)
