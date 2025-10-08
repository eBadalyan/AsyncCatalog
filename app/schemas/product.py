from pydantic import BaseModel, ConfigDict
from typing import Optional
from app.schemas.category import CategoryRead


class ProductBase(BaseModel):
    name: str
    price: float
    category_id: int

class ProductCreate(ProductBase):
    description: Optional[str] = None 
    
    is_active: Optional[bool] = True 

class ProductRead(ProductBase):
    id: int
    owner_id: int
    category: CategoryRead
    
    description: Optional[str] = None 
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
