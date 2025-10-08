import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

import sys
import os

sys.path.insert(0, os.path.realpath(".")) 

from app.config import settings

from app.database import Base
from app.models import user, product, category

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


def get_db_url() -> str:
    return settings.database_url

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    
    Uses the URL dynamically retrieved from the settings object.
    """
    # Теперь URL берется не из alembic.ini, а из Pydantic settings.
    url = get_db_url()
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    Uses the URL dynamically retrieved from the settings object.
    """
    
    # Получаем секцию настроек из alembic.ini
    ini_section = config.get_section(config.config_ini_section, {})

    # 🔑 Самый важный шаг: переопределяем 'sqlalchemy.url' динамическим значением
    # перед передачей в async_engine_from_config.
    ini_section['sqlalchemy.url'] = get_db_url()

    connectable = async_engine_from_config(
        ini_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
