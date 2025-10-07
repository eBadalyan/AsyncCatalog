from fastapi import FastAPI
from pydantic import BaseModel


class HealthMessage(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"

app = FastAPI()

@app.get("/health", response_model=HealthMessage)
async def get_health():
    return {"status": "ok", "version": "1.0.0"}