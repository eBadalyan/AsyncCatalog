from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings
from typing import AsyncGenerator


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