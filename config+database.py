#config.py
import os
import redis
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from datetime import timedelta
from fastapi_mail import ConnectionConfig

# Загружаем переменные окружения
load_dotenv()

class Settings(BaseSettings):
    # Если используешь asyncpg с SQLAlchemy, можешь указать "postgresql+asyncpg://..."
    SQLALCHEMY_DATABASE_URI: str = os.getenv("SQLALCHEMY_DATABASE_URI", "postgresql+asyncpg://postgres:898939@localhost:5432/new_db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "defaultsecretkey")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    # JWT Конфигурация
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-jwt-secret-key")  
    JWT_ACCESS_TOKEN_EXPIRES: timedelta = timedelta(days=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 7)))
    JWT_REFRESH_TOKEN_EXPIRES: timedelta = timedelta(days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", 30)))

     # 🔥 ДОБАВЬ ЭТИ:
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str
    MAIL_PORT: int
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False


    class Config:
        env_file = ".env"


settings = Settings()

MAIL_CONF = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TIMEOUT=30  # увеличиваем таймаут
)

class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI

    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
    PRODUCT_UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'goods')
    PET_UPLOAD_FOLDER     = os.path.join(BASE_DIR, 'static', 'pets')
    COSMETIC_UPLOAD_FOLDER     = os.path.join(BASE_DIR, 'static', 'cosmetic')
    FORUM_THREADS_PATH = os.path.join(BASE_DIR, "data", "forum_threads.json")
    NEWS_FILE = os.path.join(BASE_DIR, "data", "news.json")
    PRODUCTS_FILE = os.path.join(BASE_DIR, "data", "products.json")
    ACHIEVEMENTS_FILE = os.path.join(BASE_DIR, "data", "achievements.json")  # ✅ Путь к ачивкам

    for folder in [UPLOAD_FOLDER, PRODUCT_UPLOAD_FOLDER]:
        os.makedirs(folder, exist_ok=True)

    os.makedirs(os.path.dirname(NEWS_FILE), exist_ok=True)

    if not os.path.exists(NEWS_FILE):
        with open(NEWS_FILE, "w", encoding="utf-8") as f:
            f.write("[]")

    print(f"📌 NEWS_FILE загружен: {NEWS_FILE}")

try:
    REDIS_CONN = redis.StrictRedis.from_url(settings.REDIS_URL, decode_responses=False)
except redis.ConnectionError as e:
    print(f"❌ Ошибка подключения к Redis: {e}")
    REDIS_CONN = None

   
#database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings
from typing import AsyncGenerator

DATABASE_URL = settings.SQLALCHEMY_DATABASE_URI  # Используем правильный URL из config.py

engine = create_async_engine(DATABASE_URL, echo=True)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session