import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import asyncio
from sqlalchemy import select
from database import async_session
from models.models import Role

ROLES = [
    {"name": "ADMIN", "display_name": "Администратор"},
    {"name": "MODERATOR", "display_name": "Модератор"},
    {"name": "USER", "display_name": "Пользователь"},
    {"name": "TESTER", "display_name": "Тестер"},
    {"name": "AI", "display_name": "ИИ"},
]

async def seed_roles():
    async with async_session() as session:
        for role in ROLES:
            result = await session.execute(select(Role).where(Role.name == role["name"]))
            existing = result.scalar_one_or_none()
            if existing:
                existing.display_name = role["display_name"]
            else:
                session.add(Role(**role))
        await session.commit()
        print("✅ Роли сохранены")

if __name__ == "__main__":
    asyncio.run(seed_roles())
