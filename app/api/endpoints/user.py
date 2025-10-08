from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserCreate, UserRead
from app.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.models.user import User
from typing import List
from app.core.security import get_current_user, hash_password, verify_password


router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserRead)
async def create_user(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_async_session)
):
    hashed_password = hash_password(user_in.password) 
    
    user_data = user_in.model_dump(exclude={"password"})
    new_user = User(**user_data, hashed_password=hashed_password) 

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user

@router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: User = Depends(get_current_user)
):
    return current_user