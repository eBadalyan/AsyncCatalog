from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.core.roles import UserRole
from app.schemas.role import RoleRead


class UserRead(BaseModel):
    """Схема для возврата данных пользователя, включая объект роли."""
    id: int
    name: str
    email: str
    role: RoleRead

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    """Схема для регистрации нового пользователя."""
    name: str
    email: str
    password: str = Field(min_length=8, max_length=72)
    role: UserRole = UserRole.BUYER

