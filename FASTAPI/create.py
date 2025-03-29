from sqlalchemy import create_engine
from database import Base
from config import settings

engine_sync = create_engine(settings.SQLALCHEMY_DATABASE_URI.replace("+asyncpg", ""))
Base.metadata.create_all(bind=engine_sync)
