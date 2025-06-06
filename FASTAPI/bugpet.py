from models import Pet
from database import async_session

async def debug_add_pet(user_id: int):
    async with async_session() as db:
        pet = Pet(
            user_id=user_id,
            name="Дырбоёбик",
            image="pets/testpet.png",
            trait="хуёвый",
        )
        db.add(pet)
        await db.commit()
        print(f"✅ питомец создан: {pet.id}")
