import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from database import async_session
from models.models import DailyQuest

async def reset_daily_quests():
    async with async_session() as session:  # ⚠ зависит от твоего импорта
        result = await session.execute(select(DailyQuest))
        quests = result.scalars().all()

        for quest in quests:
            await session.delete(quest)

        await session.commit()
        print(f"✅ Удалено {len(quests)} ежедневных квестов.")

if __name__ == "__main__":
    asyncio.run(reset_daily_quests())
