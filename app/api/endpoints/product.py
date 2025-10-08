from fastapi import APIRouter, Depends, HTTPException
from app.schemas.product import ProductCreate, ProductRead
from app.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.product import Product
from typing import List



router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductRead)
async def create_product(
    product_in: ProductCreate, 
    session: AsyncSession = Depends(get_async_session)
):
    db_product = Product(**product_in.model_dump())
    session.add(db_product)
    await session.commit()
    await session.refresh(db_product)

    return db_product

@router.get("/", response_model=List[ProductRead])
async def read_products(
    session: AsyncSession = Depends(get_async_session)
):
    stmt = select(Product)
    products = await session.scalars(stmt)

    return products.all()

@router.get("/{product_id}")
async def read_product_by_id(
    product_id: int, 
    session: AsyncSession = Depends(get_async_session)
):
    stmt = select(Product).where(Product.id == product_id)
    product = await session.scalar(stmt)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product with id {product_id} not found"
        )
    
    return product

@router.put("/{product_id}")
async def update_product(
    product_in: ProductCreate,
    product_id: int, 
    session: AsyncSession = Depends(get_async_session)
):
    stmt = select(Product).where(Product.id == product_id)
    product = await session.scalar(stmt)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail=f"Product with id {product_id} not found"
        )
    
    product.name = product_in.name
    product.price = product_in.price

    await session.commit()
    await session.refresh(product)

    return product

@router.delete("/{product_id}")
async def delete_product(
    product_id: int, 
    session: AsyncSession = Depends(get_async_session)
):
    stmt = delete(Product).where(Product.id == product_id)
    result = await session.execute(stmt)

    if result.rowcount == 0:
        raise HTTPException(
            status_code=404,
            detail=f"Product with id {product_id} not found"
        )
    
    await session.commit()