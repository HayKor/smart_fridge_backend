from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from smart_fridge.core.exceptions.cart_product import CartProductForbiddenException, CartProductNotFoundException
from smart_fridge.lib.models import CartProductModel
from smart_fridge.lib.schemas.cart_product import (
    CartProductCreateSchema,
    CartProductPatchSchema,
    CartProductSchema,
    CartProductUpdateSchema,
)


def _raise_for_user_access(cart_product_model: CartProductModel, user_id: int) -> None:
    """Check if the user has access to the cart product.

    Args:
        cart_product_model (CartProductModel): The cart product model instance.
        user_id (int): The ID of the user.

    Raises:
        CartProductForbiddenException: If the user does not own the cart product.
    """
    if not cart_product_model.owner_id == user_id:
        raise CartProductForbiddenException


async def create_cart_product(db: AsyncSession, user_id: int, schema: CartProductCreateSchema) -> CartProductSchema:
    """Create a new cart product for the user.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        user_id (int): The ID of the user.
        schema (CartProductCreateSchema): The schema containing cart product data.

    Returns:
        CartProductSchema: The created cart product schema.
    """
    cart_product_model = CartProductModel(**schema.model_dump(), owner_id=user_id)
    db.add(cart_product_model)
    await db.flush()
    return CartProductSchema.model_construct(**cart_product_model.to_dict())


async def get_cart_products(db: AsyncSession, user_id: int) -> list[CartProductSchema]:
    """Retrieve all cart products for the user.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        user_id (int): The ID of the user.

    Returns:
        list[CartProductSchema]: A list of cart product schemas.
    """
    query = (
        select(CartProductModel)
        .where(CartProductModel.owner_id == user_id, CartProductModel.deleted_at.is_(None))
        .options(joinedload(CartProductModel.product_type))
    )
    cart_products = (await db.execute(query)).scalars().all()

    items = [CartProductSchema.model_construct(**i.to_dict()) for i in cart_products]
    return items


async def get_cart_product(db: AsyncSession, cart_product_id: int, user_id: int) -> CartProductSchema:
    """Retrieve a specific cart product by its ID for the user.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        cart_product_id (int): The ID of the cart product.
        user_id (int): The ID of the user.

    Returns:
        CartProductSchema: The cart product schema.

    Raises:
        CartProductForbiddenException: If the user does not own the cart product.
    """
    cart_product_model = await get_cart_product_model(db, cart_product_id=cart_product_id, join_product_type=True)
    _raise_for_user_access(cart_product_model, user_id)
    return CartProductSchema.model_validate(cart_product_model.to_dict())


async def get_cart_product_model(
    db: AsyncSession, cart_product_id: int, join_product_type: bool = False
) -> CartProductModel:
    """Retrieve the cart product model by its ID.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        cart_product_id (int): The ID of the cart product.
        join_product_type (bool, optional): Whether to join the product type. Defaults to False.

    Returns:
        CartProductModel: The cart product model.

    Raises:
        CartProductNotFoundException: If the cart product is not found.
    """
    query = select(CartProductModel).where(CartProductModel.id == cart_product_id)
    if join_product_type:
        query = query.options(joinedload(CartProductModel.product_type))
    result = (await db.execute(query)).scalar_one_or_none()
    if result is None:
        raise CartProductNotFoundException
    return result


async def update_cart_product(
    db: AsyncSession, cart_product_id: int, schema: CartProductUpdateSchema | CartProductPatchSchema, user_id: int
) -> CartProductSchema:
    """Update an existing cart product.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        cart_product_id (int): The ID of the cart product to update.
        schema (CartProductUpdateSchema | CartProductPatchSchema): The schema containing updated cart product data.
        user_id (int): The ID of the user.

    Returns:
        CartProductSchema: The updated cart product schema.

    Raises:
        CartProductForbiddenException: If the user does not own the cart product.
    """
    cart_product_model = await get_cart_product_model(db, cart_product_id=cart_product_id)
    _raise_for_user_access(cart_product_model, user_id)

    for field, value in schema.iterate_set_fields():
        setattr(cart_product_model, field, value)

    await db.flush()
    return CartProductSchema.model_construct(**cart_product_model.to_dict())


async def delete_cart_product(db: AsyncSession, cart_product_id: int, user_id: int) -> None:
    """Delete a cart product by marking it as deleted.

    Args:
        db (AsyncSession): Async SQLAlchemy session.
        cart_product_id (int): The ID of the cart product to delete.
        user_id (int): The ID of the user.

    Raises:
        CartProductForbiddenException: If the user does not own the cart product.
    """
    cart_product_model = await get_cart_product_model(db, cart_product_id)
    _raise_for_user_access(cart_product_model, user_id)
    cart_product_model.deleted_at = datetime.now(timezone.utc)
    await db.flush()
