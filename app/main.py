from fastapi import FastAPI
from pydantic import BaseModel
from app.database import create_db_and_tables


class HealthMessage(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    print("Создание таблиц БД...")
    await create_db_and_tables()
    print("Таблицы созданы!")

@app.get("/health", response_model=HealthMessage)
async def get_health():
    return {"status": "ok", "version": "1.0.0"}