from fastapi import FastAPI
from pydantic import BaseModel
from app.database import create_db_and_tables
from app.api.endpoints import product as product_router
from app.api.endpoints import user as user_router
from app.api.endpoints import auth as auth_router
from app.api.endpoints import category as category_router
from app.models import user, product, category


class HealthMessage(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"

app = FastAPI(title="FastAPI Catalog API")

@app.on_event("startup")
async def startup_event():
    print("Создание таблиц БД...")
    await create_db_and_tables()
    print("Таблицы созданы!")

app.include_router(product_router.router)
app.include_router(auth_router.router, tags=["Auth"])
app.include_router(user_router.router)
app.include_router(category_router.router)

@app.get("/health", response_model=HealthMessage)
async def get_health():
    return {"status": "ok", "version": "1.0.0"}