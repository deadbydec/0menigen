# delete_limit.py

import asyncio
from datetime import date
from sqlalchemy.future import select
from models.models import LandfillPickupLimit
from database import async_session  # Убедись, что ты импортируешь из своего database.py

USER_ID = 1  # <-- поменяй на нужный ID

async def delete_landfill_limit():
    async with async_session() as db:
        result = await db.execute(
            select(LandfillPickupLimit).where(
                LandfillPickupLimit.user_id == USER_ID,
                LandfillPickupLimit.date == date.today()
            )
        )
        limit = result.scalar()

        if limit:
            await db.delete(limit)
            await db.commit()
            print(f"✅ Лимит подбора для user_id={USER_ID} успешно сброшен.")
        else:
            print(f"ℹ️ Лимит для user_id={USER_ID} не найден — ничего не делаем.")

if __name__ == "__main__":
    asyncio.run(delete_landfill_limit())

