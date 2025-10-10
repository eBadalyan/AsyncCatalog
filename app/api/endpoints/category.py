from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
# Импортируем select и delete, алиасируя delete как sa_delete, чтобы избежать конфликта
from sqlalchemy import select, delete as sa_delete 

from app.database import get_async_session
from app.schemas.category import CategoryCreate, CategoryRead
from app.models.category import Category
from app.models.user import User
from app.core.security import get_current_admin

# Предполагаем, что у вас есть CategoryCreate для обновления имени
# Если у вас есть CategoryUpdate, замените CategoryCreate в PUT-маршруте на него.

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("/", response_model=CategoryRead, status_code=status.HTTP_201_CREATED, summary="Создать новую категорию (Только для Админа)")
async def create_category(
    category_in: CategoryCreate, 
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_admin) 
):
    db_category = Category(
        name=category_in.name,
        owner_id=current_user.id
    )
    
    session.add(db_category)
    await session.commit()
    await session.refresh(db_category)
    
    return db_category

@router.get("/", response_model=List[CategoryRead], summary="Получить все категории")
async def read_categories(
    session: AsyncSession = Depends(get_async_session)
):
    stmt = select(Category)
    result = await session.scalars(stmt)
    categories = result.all()
    
    return categories

@router.get("/{category_id}", response_model=CategoryRead, summary="Получить категорию по ID")
async def read_category(
    category_id: int,
    session: AsyncSession = Depends(get_async_session)
):
    stmt = select(Category).where(Category.id == category_id)
    category = await session.scalar(stmt)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    return category

# --- НОВЫЙ МАРШРУТ: РЕДАКТИРОВАНИЕ (PUT) ---
@router.put("/{category_id}", response_model=CategoryRead, summary="Обновить категорию (Только для Админа)")
async def update_category(
    category_id: int,
    category_in: CategoryCreate, # Принимаем новую информацию (минимум, имя)
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_admin)
):
    # 1. Находим категорию
    stmt = select(Category).where(Category.id == category_id)
    category = await session.scalar(stmt)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
        
    # 2. Обновляем данные
    category.name = category_in.name
    
    session.add(category)
    await session.commit()
    await session.refresh(category)
    
    return category

# --- НОВЫЙ МАРШРУТ: УДАЛЕНИЕ (DELETE) ---
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить категорию (Только для Админа)")
async def delete_category(
    category_id: int,
    session: AsyncSession = Depends(get_async_session),
    current_user: User = Depends(get_current_admin) # Проверка прав Администратора
):
    # 1. Проверяем существование категории перед удалением
    stmt_check = select(Category).where(Category.id == category_id)
    category = await session.scalar(stmt_check)
    
    if not category:
        # Важно: если не найдено, возвращаем 404, а не 405
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # 2. Удаляем категорию
    # Используем sa_delete для выполнения команды DELETE
    stmt_delete = sa_delete(Category).where(Category.id == category_id)
    await session.execute(stmt_delete)
    
    # 3. Фиксируем изменения
    await session.commit()
    
    # Возвращаем 204 No Content (успешное удаление без тела ответа)
    return 
