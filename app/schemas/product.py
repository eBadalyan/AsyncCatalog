from pydantic import BaseModel, ConfigDict


class ProductRead(BaseModel):
    id: int
    name: str
    price: float

    model_config = ConfigDict(from_attributes=True)


class ProductCreate(BaseModel):
    name: str
    price: float