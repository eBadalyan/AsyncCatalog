from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings
from typing import AsyncGenerator
from app.models.base import Base
from app.models.product import Product


engine = create_async_engine(
    settings.daatabase_url, 
    echo=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    session: AsyncSession = await AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)