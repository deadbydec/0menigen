import sys
import os
import asyncio
import json
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from database import async_session
from models.models import Race

# сделаем:
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))  # выходим из scripts/
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "races.json")

async def seed():
    with open(DATA_PATH, "r", encoding="utf-8") as f:
        race_data = json.load(f)

    async with async_session() as session:
        for race in race_data:
            stmt = select(Race).where(Race.code == race["code"])
            result = await session.execute(stmt)
            existing = result.scalar_one_or_none()

            if existing:
                for key, value in race.items():
                    setattr(existing, key, value)
                print(f"🔁 Обновлена раса: {race['code']}")
            else:
                session.add(Race(**race))
                print(f"✨ Добавлена новая раса: {race['code']}")

        await session.commit()
        print("✅ Синхронизация рас завершена.")

if __name__ == "__main__":
    asyncio.run(seed())


