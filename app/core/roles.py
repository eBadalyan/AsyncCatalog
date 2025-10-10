from enum import Enum

class UserRole(str, Enum):
    """
    Определение доступных ролей пользователей. 
    Используется в Pydantic схемах и в логике авторизации.
    """
    ADMIN = "admin"
    SELLER = "seller"
    BUYER = "buyer"
