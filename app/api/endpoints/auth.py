from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from sqlalchemy import select
from app.database import get_async_session
from app.core.security import create_access_token, verify_password, hash_password
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/auth/jwt", tags=["Tokens"])

@router.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session)
):
    stmt = select(User).where(User.email == form_data.username)
    user = await session.scalar(stmt)

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail=f"Incorrect username or password"
        )
    
    access_token = create_access_token(data={"sub": user.email})

    return {"access_token": access_token, "token_type": "bearer"}