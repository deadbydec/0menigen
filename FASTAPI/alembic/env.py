import importlib
import pkgutil
from models import Base # ✅ Должен подтянуться `models.py`
import models
import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from alembic import context
from database import Base, DATABASE_URL  # Импортируем базу и URL из database.py
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from config import settings

# Загружаем настройки логирования из alembic.ini
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Подключаем MetaData из моделей, чтобы Alembic понимал, какие таблицы отслеживать
target_metadata = Base.metadata
print(f"📌 Alembic видит эти таблицы: {Base.metadata.tables.keys()}")

# Автоматически подгружаем все модели, чтобы Alembic их видел
def import_all_models():
    """Импортирует все файлы в папке models/"""
    for _, module_name, _ in pkgutil.iter_modules(models.__path__):  # Теперь не будет ошибки
        importlib.import_module(f"models.{module_name}")

import_all_models()


# Создаём асинхронный движок для PostgreSQL с нужными опциями
def get_engine() -> AsyncEngine:
    return create_async_engine(
        settings.SQLALCHEMY_DATABASE_URI,  # Используем DSN из настроек, например "postgresql+asyncpg://..."
        echo=True,
        pool_pre_ping=True,
        poolclass=NullPool,  # Отключаем пул соединений, чтобы избежать проблем с переиспользованием
        future=True
    )

# ОФФЛАЙН-режим (если запускаем Alembic без доступа к БД)
def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


# Функция, выполняющая миграции в синхронном режиме внутри асинхронного контекста
def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

# ОНЛАЙН-режим (обычный режим работы)
async def run_migrations_online():
    engine = get_engine()
    async with engine.connect() as connection:
        # Запускаем миграции в синхронном контексте
        await connection.run_sync(do_run_migrations)
    # Закрываем движок после завершения миграций
    await engine.dispose()

if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

