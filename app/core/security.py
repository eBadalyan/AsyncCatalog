from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from typing import Optional, List
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials # <-- ДОБАВЛЕН HTTPBearer и HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_async_session
from app.models.user import User
from app.core.roles import UserRole
from sqlalchemy import select
from sqlalchemy.orm import selectinload

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Хэширует пароль."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля хэшу."""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Создает JWT токен доступа."""
    to_encode = data.copy() 

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire}) 
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

# oauth2_cheme оставлен для совместимости, но не будет использоваться в get_current_user
oauth2_cheme = OAuth2PasswordBearer(tokenUrl="token") 
bearer_scheme = HTTPBearer() # <-- НОВАЯ СХЕМА ДЛЯ РУЧНОГО ВВОДА

async def get_current_user(
        # Изменяем зависимость на bearer_scheme, который возвращает объект с токеном
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        session: AsyncSession = Depends(get_async_session)
):
    """Зависимость: Извлекает пользователя из JWT токена."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    
    # Извлекаем сам токен из объекта credentials
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_email = payload.get("sub")

        if user_email is None:
            raise credentials_exception
        
    except JWTError:
        raise credentials_exception
    
    stmt = (
        select(User)
        .where(User.email == user_email)
        .options(selectinload(User.role))
    )
    user = await session.scalar(stmt)
    
    if user is None:
        raise credentials_exception
        
    return user

# --- УНИВЕРСАЛЬНЫЕ ЗАВИСИМОСТИ ДЛЯ ПРОВЕРКИ РОЛЕЙ ---

def role_checker(required_roles: List[UserRole]):
    """
    Создает зависимость, проверяющую, соответствует ли роль текущего 
    пользователя одной из требуемых ролей.
    """
    def check_roles(current_user: User = Depends(get_current_user)) -> User:
        required_role_values = [role.value for role in required_roles]
        
        # Проверка, что current_user.role является объектом, а не простым значением
        # и доступ к имени роли через .name
        if current_user.role.name not in required_role_values:
             raise HTTPException(
                 status_code=status.HTTP_403_FORBIDDEN,
                 detail=f"Недостаточно прав. Требуется одна из ролей: {', '.join(required_role_values)}."
             )

        return current_user
    return check_roles

get_current_admin = role_checker([UserRole.ADMIN])
get_current_seller = role_checker([UserRole.SELLER])
get_seller_or_admin = role_checker([UserRole.SELLER, UserRole.ADMIN])
get_buyer = role_checker([UserRole.BUYER])
