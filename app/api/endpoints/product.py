from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_seller_or_admin
from app.models.user import User
from app.schemas.product import ProductCreate, ProductRead 
from app.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload
from app.models.product import Product
from app.models.category import Category
from typing import List, Optional 

router = APIRouter(prefix="/products", tags=["Products"])

def select_product_with_category():
    """Возвращает SELECT-запрос с жадной загрузкой отношения category."""
    return select(Product).options(selectinload(Product.category))


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_in: ProductCreate, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_seller_or_admin)
):
    """Создать новый продукт. Требуется авторизация."""
    
    stmt_category = select(Category).where(Category.id == product_in.category_id)
    category = await session.scalar(stmt_category)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with ID {product_in.category_id} not found"
        )
    
    db_product = Product(
        owner_id=current_user.id, 
        **product_in.model_dump()
    )

    session.add(db_product)
    await session.commit()

    stmt_eager = select_product_with_category().where(Product.id == db_product.id)
    result = await session.execute(stmt_eager)
    product_with_category = result.scalars().first()
    
    if not product_with_category:
        raise HTTPException(status_code=500, detail="Error retrieving created product.")

    return product_with_category 


@router.get("/", response_model=List[ProductRead])
async def read_products(
    session: AsyncSession = Depends(get_async_session)
):
    """Получить список всех продуктов с жадной загрузкой категорий."""
    
    stmt = select_product_with_category()
    result = await session.scalars(stmt)

    return result.all()


@router.get("/{product_id}", response_model=ProductRead)
async def read_product_by_id(
    product_id: int, 
    session: AsyncSession = Depends(get_async_session)
):
    """Получить продукт по ID с жадной загрузкой категории."""
    
    stmt = select_product_with_category().where(Product.id == product_id)
    product = await session.scalar(stmt)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product with id {product_id} not found"
        )
    
    return product


@router.put("/{product_id}", response_model=ProductRead)
async def update_product(
    product_id: int, 
    product_in: ProductCreate, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_seller_or_admin) 
):
    """Обновить существующий продукт. Только владелец может это сделать."""
    
    stmt_select = select(Product).where(Product.id == product_id)
    product = await session.scalar(stmt_select)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product with id {product_id} not found"
        )
    
    if product.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this product."
        )

    if product_in.category_id:
        category = await session.scalar(
            select(Category).where(Category.id == product_in.category_id)
        )
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Category with ID {product_in.category_id} not found"
            )

    update_data = product_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(product, key, value) 
    
    await session.commit()

    stmt_eager = select_product_with_category().where(Product.id == product.id)
    result = await session.execute(stmt_eager)
    updated_product_with_category = result.scalars().first()
    
    if not updated_product_with_category:
        raise HTTPException(status_code=500, detail="Error retrieving updated product.")

    return updated_product_with_category


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_seller_or_admin) 
):
    """Удалить продукт. Только владелец может это сделать."""
    
    stmt_select = select(Product).where(Product.id == product_id)
    product = await session.scalar(stmt_select)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product with id {product_id} not found"
        )

    if product.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this product."
        )

    stmt_delete = delete(Product).where(Product.id == product_id)
    await session.execute(stmt_delete)
    await session.commit()
    
    return