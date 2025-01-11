from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from smart_fridge.core.exceptions.cart_product import CartProductlAlreadyExistsException
from smart_fridge.lib.models import CartProductModel
from smart_fridge.lib.schemas.cart_product import CartProductCreateSchema, CartProductSchema


async def create_cart_product(db: AsyncSession, user_id: int, schema: CartProductCreateSchema) -> CartProductSchema:
    cart_product_model = CartProductModel(**schema.model_dump(), owner_id=user_id)
    db.add(cart_product_model)
    await db.flush()
    return CartProductSchema.model_construct(**cart_product_model.to_dict())


async def is_product_exists(db: AsyncSession, product_type_id: int) -> bool:
    query = select(CartProductModel).where(CartProductModel.product_type_id == product_type_id)
    return bool((await db.execute(query)).scalar_one_or_none())


async def raise_for_product(db: AsyncSession, product_type_id: int) -> None:
    if await is_product_exists(db, product_type_id):
        raise CartProductlAlreadyExistsException(product_id=product_type_id)
