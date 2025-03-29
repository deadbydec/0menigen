import json
import enum
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime, select, JSON
from sqlalchemy.dialects.postgresql import INET
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from config import Config
from sqlalchemy.orm import selectinload
from sqlalchemy import Enum as SqlEnum
from database import async_session, Base  # ✅ Теперь используется правильный sessionmaker!