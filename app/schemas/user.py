from pydantic import BaseModel, ConfigDict, Field


class UserRead(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class UserCreate(BaseModel):
    name: str
    email: str
    password: str = Field(min_length=8, max_length=72)