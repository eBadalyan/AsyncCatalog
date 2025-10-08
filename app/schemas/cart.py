# schemas/cart.py
from pydantic import BaseModel, ConfigDict
from app.schemas.product import ProductRead
from typing import List


class CartItemCreate(BaseModel):
    product_id: int
    quantity: int = 1

class CartItemRead(BaseModel):
    id: int
    product_id: int
    quantity: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)

class CartItemReadWithProduct(CartItemRead):
    product: ProductRead

class CartRead(BaseModel):
    items: List[CartItemReadWithProduct]
    total_price: float