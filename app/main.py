from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import product as product_router
from app.api.endpoints import user as user_router
from app.api.endpoints import auth as auth_router
from app.api.endpoints import category as category_router
from app.api.endpoints import cart as cart_router
from app.models import user, product, category, cart


app = FastAPI(title="FastAPI Catalog API")

origins = [
    "*", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("Приложение стартует. Схема БД управляется Alembic.")


app.include_router(product_router.router)
app.include_router(auth_router.router, tags=["Auth"])
app.include_router(user_router.router)
app.include_router(category_router.router)
app.include_router(cart_router.router)

app.mount("/static", StaticFiles(directory="app/frontend"), name="static")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    try:
        with open("app/frontend/index.html", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<html><body><h1>Файл index.html не найден!</h1></body></html>"
