from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_async_session
from app.schemas.category import CategoryCreate, CategoryRead
from app.models.category import Category
from app.models.user import User
from app.core.security import get_current_user

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_user) 
):    
    db_category = Category(
        name=category_in.name,
        owner_id=current_user.id
    )
    
    session.add(db_category)
    await session.commit()
    await session.refresh(db_category)
    
    return db_category

@router.get("/", response_model=List[CategoryRead])
async def read_categories(
    session: AsyncSession = Depends(get_async_session)
):    
    stmt = select(Category)
    result = await session.scalars(stmt)
    categories = result.all()
    
    return categories

@router.get("/{category_id}", response_model=CategoryRead)
async def read_category(
    category_id: int,
    session: AsyncSession = Depends(get_async_session)
):    
    stmt = select(Category).where(Category.id == category_id)
    category = await session.scalar(stmt)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category