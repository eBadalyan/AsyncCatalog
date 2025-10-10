from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import UserCreate, UserRead
from app.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.models.role import Role
from app.core.security import hash_password, get_current_user
from app.core.roles import UserRole
from sqlalchemy.orm import selectinload

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserRead)
async def create_user(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_async_session)
):
    """Создает нового пользователя. По умолчанию роль - buyer или seller (если выбрано)."""

    if user_in.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Невозможно зарегистрироваться с ролью admin. Используйте 'buyer' или 'seller'."
        )

    existing_user = await session.scalar(select(User).where(User.email == user_in.email))
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    role_name = user_in.role.value 
    
    role_db = await session.scalar(
        select(Role).where(Role.name == role_name)
    )
    
    if not role_db:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Роль '{role_name}' не найдена в базе данных. Убедитесь, что миграции Alembic запущены."
        )

    hashed_password = hash_password(user_in.password) 
    
    new_user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hashed_password,
        role_id=role_db.id 
    ) 

    session.add(new_user)
    await session.commit()
    
    user_with_role = await session.scalar(
        select(User)
        .where(User.id == new_user.id)
        .options(selectinload(User.role))
    )
    
    if not user_with_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Не удалось получить созданного пользователя с его ролью."
        )

    return user_with_role

# --- ТЕСТОВЫЙ МАРШРУТ ДЛЯ ПРОВЕРКИ РОЛИ ---

@router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получает информацию о текущем пользователе. 
    Используется для проверки того, что ORM и аутентификация корректно считывают роль.
    """

    user_with_role = await session.scalar(
        select(User)
        .where(User.id == current_user.id)
        .options(selectinload(User.role))
    )

    if not user_with_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден."
        )
        
    return user_with_role

@router.get("/{user_id}", response_model=UserRead)
async def get_user_by_id(
    user_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Получает публичную информацию о пользователе по его ID (для отображения имени продавца в каталоге).
    """
    
    # Загружаем пользователя по ID, используя selectinload для роли.
    user = await session.scalar(
        select(User)
        .where(User.id == user_id)
        .options(selectinload(User.role))
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found."
        )
        
    return user


