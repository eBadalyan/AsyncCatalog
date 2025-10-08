from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, UserRead
from app.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.core.security import hash_password


router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserRead)
async def create_user(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """Создает нового пользователя. По умолчанию роль - buyer."""

    existing_user = await session.scalar(select(User).where(User.email == user_in.email))
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    hashed_password = hash_password(user_in.password) 
    
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hashed_password,
        role=user_in.role
    ) 

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user