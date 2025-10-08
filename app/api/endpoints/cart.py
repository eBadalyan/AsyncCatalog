from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from sqlalchemy.orm import selectinload

from app.database import get_async_session
from app.models.user import User
from app.models.product import Product
from app.models.cart import CartItem
from app.schemas.cart import CartItemCreate, CartRead, CartItemReadWithProduct
from app.core.security import get_current_user # Покупателям достаточно быть аутентифицированными

router = APIRouter(prefix="/cart", tags=["Cart"])

async def get_cart_with_products(user_id: int, session: AsyncSession) -> List[CartItemReadWithProduct]:
    """Получает элементы корзины пользователя с деталями продуктов."""
    stmt = (
        select(CartItem)
        .where(CartItem.user_id == user_id)
        .options(selectinload(CartItem.product).selectinload(Product.category))
    )
    result = await session.scalars(stmt)
    cart_items = result.all()
    
    cart_items_read = [
        CartItemReadWithProduct.model_validate(item, from_attributes=True)
        for item in cart_items
    ]
    
    return cart_items_read


@router.post("/", response_model=CartRead, status_code=status.HTTP_201_CREATED)
async def add_item_to_cart(
    cart_item_in: CartItemCreate,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Добавить товар в корзину или обновить его количество."""

    product = await session.scalar(select(Product).where(Product.id == cart_item_in.product_id))
    if not product or not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {cart_item_in.product_id} not found or inactive."
        )

    existing_item = await session.scalar(
        select(CartItem).where(
            CartItem.user_id == current_user.id,
            CartItem.product_id == cart_item_in.product_id
        )
    )

    if existing_item:
        existing_item.quantity += cart_item_in.quantity
    else:
        new_item = CartItem(
            user_id=current_user.id,
            product_id=cart_item_in.product_id,
            quantity=cart_item_in.quantity
        )
        session.add(new_item)

    await session.commit()
    
    cart_items_read = await get_cart_with_products(current_user.id, session)
    total_price = sum(item.product.price * item.quantity for item in cart_items_read)

    return {"items": cart_items_read, "total_price": total_price}

@router.get("/", response_model=CartRead)
async def read_cart(
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user)
):
    """Получить содержимое корзины текущего пользователя."""
    
    cart_items_read = await get_cart_with_products(current_user.id, session)
    total_price = sum(item.product.price * item.quantity for item in cart_items_read)
    
    return {"items": cart_items_read, "total_price": total_price}

# Добавьте также эндпоинт для удаления/очистки корзины, если нужно.