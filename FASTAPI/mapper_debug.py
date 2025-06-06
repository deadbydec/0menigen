# fix_slot.py
import asyncio
from sqlalchemy import update
from database import async_session
from models.models import UserPetWardrobeItem

async def fix_slot():
    async with async_session() as db:
        await db.execute(
            update(UserPetWardrobeItem)
            .where(UserPetWardrobeItem.slot == "аксессуар", UserPetWardrobeItem.product_id == 167)
            .values(slot="фон")
        )
        await db.commit()
        print("✅ Слот обновлён!")

if __name__ == "__main__":
    asyncio.run(fix_slot())

